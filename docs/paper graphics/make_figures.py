"""Generate the Spock paper schematics as SVG (then render_figures.sh -> PNG/PDF).

Sized for HALF AN A4 PAGE: canvas 960 units wide, printed at 170 mm text width
(1 unit ~ 0.177 mm). Font floor 13 units (~6.5 pt); body 14-16 (~7-8 pt).

Fig 1  fig1_concepts.svg - threats to validity in AI-assisted research, each paired with
                           the Spock concept that counters it (verbatim skill excerpts).
Fig 2  fig2_process.svg  - the research arc: Plan -> Run, gates, critic passes.

Colours: dataviz reference palette (light). Role encoding fixed across figures:
  researcher = orange, kg-coder = aqua, critic = violet, KG = blue, commits / discipline = ink.

Run:  uv run python "docs/paper graphics/make_figures.py"
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

INK, INK2, LINE, BG = "#0b0b0b", "#52514e", "#c9c8c2", "#ffffff"
BLUE, ORANGE, AQUA, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#e34948"
AQUA_TXT = "#0d7a53"  # aqua darkened for text on white
FONT = "Helvetica, Arial, 'Segoe UI', sans-serif"
MIN_FONT = 13


def tint(hex_, a):
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = lambda c: round(255 - (255 - c) * a)
    return f"#{m(r):02x}{m(g):02x}{m(b):02x}"


def wrap(s, width, size, k=0.5):
    n = max(8, int(width / (size * k)))
    lines, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + ([cur] if cur else [])


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.parts = w, h, []
        self.colors = {INK, INK2, BLUE, ORANGE, AQUA, AQUA_TXT, VIOLET, RED}

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, stroke=LINE, fill=BG, rx=8, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=14, weight="normal", fill=INK, anchor="start", style="normal"):
        assert size >= MIN_FONT, (s, size)
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
                 f'font-style="{style}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')

    def para(self, x, y, s, width, size=14, lh=1.28, **kw):
        lines = wrap(s, width, size)
        for i, ln in enumerate(lines):
            self.text(x, y + i * size * lh, ln, size=size, **kw)
        return y + len(lines) * size * lh

    def arrow(self, pts, color=INK2, sw=1.8, dash=None, both=False, curve=False):
        cid = color.lstrip("#")
        d = f' stroke-dasharray="{dash}"' if dash else ""
        if curve:
            (x1, y1), (a, b), (c, e), (x2, y2) = pts
            path = f"M{x1},{y1} C{a},{b} {c},{e} {x2},{y2}"
        else:
            path = "M" + " L".join(f"{x},{y}" for x, y in pts)
        st = f' marker-start="url(#m{cid})"' if both else ""
        self.add(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} '
                 f'marker-end="url(#m{cid})"{st}/>')

    def save(self, name):
        markers = "".join(
            f'<marker id="m{c.lstrip("#")}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            f'markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'fill="{c}"/></marker>' for c in self.colors)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}"><defs>{markers}</defs>'
               f'<rect width="100%" height="100%" fill="{BG}"/>' + "\n".join(self.parts) + "</svg>")
        (OUT / name).write_text(svg, encoding="utf-8")
        print("wrote", OUT / name)


CONCEPT_COLORS = [BLUE, ORANGE, AQUA_TXT, VIOLET, INK, INK]   # Fig 1 rows 1-6
CONCEPT_SHORT = ["KG is the only data source", "pre-registered framing",
                 "doing split from judging", "fresh-context critic",
                 "describe before interpreting", "scripts + full history"]


def cbadge(s, cx, cy, n):
    """Numbered concept badge (n = Fig 1 row, 1-based)."""
    s.add(f'<circle cx="{cx}" cy="{cy}" r="10.5" fill="{CONCEPT_COLORS[n - 1]}" '
          f'stroke="#fff" stroke-width="1.5"/>')
    s.text(cx, cy + 4.5, str(n), size=13, weight="bold", fill="#fff", anchor="middle")


# ---------------------------------------------------------------- Figure 1
# (risk, risk gloss, concept, concept colour, quote, source)
ROWS = [
    ("Facts from model memory",
     "gene names, values and experiments recalled, not queried",
     "The KG is the sole data source", BLUE,
     "Every claim must trace to a KG query. Never rely on intrinsic knowledge for data.",
     "Rule 1 · findings tagged [KG] / [interpretation] / [gap]"),
    ("Confirming the hoped-for result",
     "success criteria chosen after the data are seen",
     "Pre-registered framing, locked before data", ORANGE,
     "…a pre-registered expected-negative — a class that should not score if the signal is "
     "genuine.",
     "Rule 8 · also a statistics plan and a named validation set"),
    ("Narrated, not measured",
     "a summary says “all 5 are UP”; the data file disagrees",
     "Execution separated from judgment", AQUA_TXT,
     "You execute; the main thread judges. You return artifacts, not conclusions.",
     "kg-coder agent · the judge reads the real files"),
    ("Grading one's own story",
     "the author cannot see the holes in their own narrative",
     "Independent fresh-context critic", VIOLET,
     "The author who wrote the story cannot reliably see its holes; a fresh reader of the "
     "data files can.",
     "critic gate · Blockers resolved before the researcher sees the work"),
    ("Overclaiming",
     "the language outruns the evidence",
     "Describe before interpreting", INK,
     "Words like “all”, “every”, “systematically” … require a query against the data file, "
     "not a heatmap glance.",
     "Rule 9 · “striking”, “central finding” banned until evaluation"),
    ("Untraceable results",
     "arithmetic in chat; analyses silently revised",
     "Scripts and a complete history", INK,
     "Chat-computed statistics are unreproducible — they can't be rerun, verified, or shared.",
     "Rule 5 · every iteration committed, never amended"),
]


def figure1():
    s = SVG(960, 694)
    xr, wr = 12, 300          # risk column
    xc, wc = 352, 596         # concept column
    s.text(xr + 4, 28, "Threat to validity", size=16, weight="bold", fill=RED)
    s.text(xc + 4, 28, "Spock concept — in the skill's own words", size=16, weight="bold")

    y, rh, gap = 42, 92, 8
    for n, (risk, gloss, concept, c, quote, src) in enumerate(ROWS, 1):
        s.rect(xr, y, wr, rh, stroke="none", fill=tint(RED, 0.07))
        s.add(f'<rect x="{xr}" y="{y}" width="4" height="{rh}" fill="{RED}"/>')
        s.text(xr + 16, y + 30, risk, size=16, weight="bold")
        s.para(xr + 16, y + 54, gloss, wr - 30, size=14, fill=INK2)

        s.arrow([(xr + wr + 6, y + rh / 2), (xc - 8, y + rh / 2)], INK2, sw=2)

        s.rect(xc, y, wc, rh, stroke=c, fill=tint(c, 0.06), sw=1.5)
        s.add(f'<rect x="{xc}" y="{y}" width="4" height="{rh}" fill="{c}"/>')
        s.text(xc + 16, y + 25, concept, size=16, weight="bold", fill=c)
        cbadge(s, xc + wc - 20, y + 20, n)
        yy = s.para(xc + 16, y + 47, f"“{quote}”", wc - 30, size=14, style="italic")
        s.text(xc + 16, yy + 1, src, size=13, fill=INK2)
        y += rh + gap

    s.rect(xr, y + 4, xc + wc - xr, 38, stroke=ORANGE, fill=tint(ORANGE, 0.08), rx=19)
    s.text((xr + xc + wc) / 2, y + 28, "Throughout: the researcher agrees each step's scope "
           "and approves it; the assistant never closes a step alone.",
           size=14, weight="bold", fill=INK, anchor="middle")
    s.save("fig1_concepts.svg")


# ---------------------------------------------------------------- Figure 2
def figure2():
    s = SVG(960, 646)
    ph = 634
    s.rect(6, 6, 352, ph, stroke="none", fill="#f5f5f3", rx=10)
    s.rect(368, 6, 586, ph, stroke="none", fill="#f5f5f3", rx=10)
    s.text(22, 38, "PLAN", size=20, weight="bold")
    s.text(86, 38, "→ proposal.md", size=15, fill=INK2)
    s.text(384, 38, "RUN", size=20, weight="bold")
    s.text(436, 38, "three milestones", size=15, fill=INK2)

    def step(y, h, num, title):
        s.rect(20, y, 324, h, stroke=LINE, fill=BG)
        s.add(f'<circle cx="40" cy="{y + 21}" r="11" fill="{INK}"/>')
        s.text(40, y + 26, str(num), size=13, weight="bold", fill="#fff", anchor="middle")
        s.text(58, y + 27, title, size=16, weight="bold")

    step(56, 42, 1, "Question, locked")
    step(112, 42, 2, "KG entries, from the KG")
    step(168, 188, 3, "Framing, enumerated")
    for i, it in enumerate(["Hypothesis", "Approach", "Statistics plan",
                            "Validation set (named genes)", "Falsifiability + expected-negative",
                            "Design comparability"]):
        s.text(58, 222 + i * 22, "• " + it, size=15)
    for y in (98, 154, 356):
        s.arrow([(182, y + 1), (182, y + 13)], INK2)

    step(370, 172, 4, "Review before execution")
    for t, c, x, y in [("Self-review", INK2, 32, 410), ("Critic", VIOLET, 186, 410),
                       ("Delta critic", VIOLET, 32, 470), ("Design review", ORANGE, 186, 470)]:
        s.rect(x, y, 146, 40, stroke=c, fill=tint(c, 0.08), sw=2, rx=6)
        s.text(x + 73, y + 25, t, size=15, weight="bold", fill=INK if c == INK2 else c,
               anchor="middle")
    s.arrow([(179, 430), (185, 430)], INK2)
    s.arrow([(259, 451), (259, 469)], INK2)
    s.arrow([(185, 490), (179, 490)], ORANGE)
    s.arrow([(105, 511), (105, 528), (259, 528), (259, 512)], VIOLET)
    s.text(182, 524, "repeat until no change", size=13, fill=VIOLET, anchor="middle")
    s.arrow([(182, 543), (182, 557)], INK2)

    s.rect(20, 558, 324, 44, stroke=INK, fill=INK, rx=22)
    s.text(182, 586, "proposal locked (approval commit)", size=15, weight="bold",
           fill="#fff", anchor="middle")
    s.arrow([(345, 580), (362, 580), (362, 112), (382, 112)], INK, sw=2)

    ms = [("methods", "build the method; toy-tested", "critic if it emits data"),
          ("analysis", "run it: scores, figures", "critic: data + interpretation"),
          ("evaluation", "assess vs. framing; write paper", "critic: interpretation")]
    for i, (n, what, crit) in enumerate(ms):
        x = 384 + i * 190
        s.rect(x, 56, 172, 138, stroke=INK, fill=BG, sw=2)
        s.text(x + 12, 80, n, size=17, weight="bold")
        yy = s.para(x + 12, 102, what, 150, size=14)
        s.para(x + 12, yy + 2, crit, 150, size=13, fill=VIOLET)
        s.rect(x + 12, 176, 9, 9, stroke="none", fill=INK, rx=2)
        s.text(x + 26, 185, "approval commit", size=13, fill=INK2)
        if i < 2:
            s.arrow([(x + 173, 116), (x + 188, 116)], INK, sw=2)

    s.add(f'<path d="M470,195 L470,200 L850,200 L850,195 M660,200 L660,204" fill="none" '
          f'stroke="{INK2}" stroke-width="1.5"/>')
    s.rect(384, 204, 552, 300, stroke=LINE, fill=BG)
    s.text(398, 230, "Inside every milestone", size=16, weight="bold")

    loop = [("co-define", "researcher agrees the scope", ORANGE),
            ("do", "kg-coder runs it", AQUA),
            ("show", "tables, figures, reports", AQUA),
            ("explore", "follow the results", AQUA),
            ("decide", "researcher approves", ORANGE)]
    xs = [392 + i * 109 for i in range(5)]
    s.text(xs[0] + 49, 270, "researcher", size=13, weight="bold", fill=ORANGE, anchor="middle")
    s.text(xs[4] + 49, 270, "researcher", size=13, weight="bold", fill=ORANGE, anchor="middle")
    s.add(f'<path d="M{xs[1]},274 L{xs[1]},266 L{xs[3] + 98},266 L{xs[3] + 98},274" '
          f'fill="none" stroke="{AQUA}" stroke-width="1.5"/>')
    s.text(xs[2] + 49, 259, "delegated: artifacts, not conclusions", size=13, weight="bold",
           fill=AQUA_TXT, anchor="middle")
    for i, (t, sub, c) in enumerate(loop):
        x = xs[i]
        s.rect(x, 280, 98, 100, stroke=c, fill=tint(c, 0.1), sw=2)
        s.text(x + 49, 303, t, size=15, weight="bold", fill=AQUA_TXT if c == AQUA else c,
               anchor="middle")
        yy = 324
        for ln in wrap(sub, 86, 13):
            s.text(x + 49, yy, ln, size=13, anchor="middle")
            yy += 16
        if i < 4:
            s.arrow([(x + 99, 330), (x + 108, 330)], INK2, sw=2)

    s.arrow([(xs[3] + 49, 381), (xs[3] + 20, 430), (xs[1] + 78, 430), (xs[1] + 49, 381)],
            AQUA_TXT, curve=True)
    s.text(xs[2] + 49, 452, "iterate; every round committed", size=13, fill=AQUA_TXT,
           anchor="middle")
    s.rect(xs[4] - 24, 400, 132, 52, stroke=VIOLET, fill=tint(VIOLET, 0.08), sw=2, rx=6)
    s.arrow([(xs[4] + 49, 400), (xs[4] + 49, 382)], VIOLET, sw=2)
    for j, ln in enumerate(["critic before", "results are shown"]):
        s.text(xs[4] + 42, 422 + j * 17, ln, size=13, fill=VIOLET, anchor="middle")
    s.text(398, 490, "Exploration may exceed the plan; findings still pass the decide gate.",
           size=13, fill=INK2, style="italic")

    s.rect(384, 518, 552, 70, stroke=ORANGE, fill=BG, dash="6,4")
    s.text(398, 543, "Reopen:", size=15, weight="bold", fill=ORANGE)
    s.para(462, 543, "data that contradicts the locked proposal reopens it; the original, "
           "the reveal and the revision are all recorded.", 462, size=14)

    lx = 384
    for label, c in [("researcher gate", ORANGE), ("kg-coder", AQUA),
                     ("critic (fresh context)", VIOLET), ("commit", INK)]:
        s.rect(lx, 606, 14, 14, stroke="none", fill=c, rx=3)
        s.text(lx + 20, 618, label, size=14, fill=INK2)
        lx += 20 + len(label) * 7.2 + 24
    s.save("fig2_process.svg")


# ---------------------------------------------------------------- Figure 2b
# Concepts (rows, = Fig 1 rows) translated into the workflow (columns).
STAGES = [("Plan", "question, KG entries, framing"),
          ("Execute", "do, show, explore (kg-coder)"),
          ("Review", "critic, before the researcher sees results"),
          ("Decide & record", "researcher approves; commit")]
LANES = [  # one cell per stage; None = the concept has no mechanism at that stage
    ("KG is the only data source",
     ["KG entries enumerated from the KG, not memory", "every number comes from a KG query",
      "critic spot-checks claims in the KG", "findings tagged [KG], [interpretation] or [gap]"]),
    ("Pre-registered framing",
     ["test, validation set and expected-negative fixed before data",
      "method built to the locked approach",
      "results judged against validation set and expected-negative",
      "plan changes only by a recorded reopen"]),
    ("Doing split from judging",
     [None, "kg-coder returns artifacts, not conclusions",
      "judge reads the real files, not summaries", "only the main thread writes the notebook"]),
    ("Fresh-context critic",
     ["critic on the proposal; delta pass after each change", None,
      "cold reader per milestone; Blockers resolved first",
      "claims added after review get a delta pass"]),
    ("Describe before interpreting",
     [None, "numbers and direction first",
      "“all”, “every” checked against the data file",
      "tables, not prose; strong words only at evaluation"]),
    ("Scripts + full history",
     ["each design-review round committed", "all computation in scripts, not chat",
      "critic findings and dispositions saved", "every iteration committed, never amended"]),
]
RESEARCHER = ["design review: shapes the plan", "co-define: scope agreed before work",
              "sees work only after the critic", "explicit approval closes each step"]


def figure2b():
    s = SVG(960, 700)
    lx, lw = 12, 196                       # concept label column
    cx0, cw, cg = 218, 176, 8              # stage columns
    cols = [cx0 + i * (cw + cg) for i in range(4)]

    # correction loop over the header
    s.arrow([(cols[3] + cw / 2, 56), (cols[3] + cw / 2, 34), (cols[0] + cw / 2, 34),
             (cols[0] + cw / 2, 54)], INK2, sw=1.8)
    s.add(f'<rect x="{cols[1] + 8}" y="22" width="{2 * cw - 16}" height="22" fill="{BG}"/>')
    s.text((cols[1] + cols[2] + cw) / 2, 38, "corrections loop back: iterate, redo, reopen; "
           "all recorded", size=13, fill=INK2, anchor="middle", style="italic")

    for i, (name, sub) in enumerate(STAGES):
        x, y, h = cols[i], 58, 36
        notch = 0 if i == 0 else 12
        pts = [(x, y), (x + cw - 4, y), (x + cw + 8, y + h / 2), (x + cw - 4, y + h),
               (x, y + h), (x + notch, y + h / 2)]
        s.add('<polygon points="' + " ".join(f"{a},{b}" for a, b in pts) + f'" fill="{INK}"/>')
        s.text(x + cw / 2 + 2, y + 24, name, size=16, weight="bold", fill="#fff", anchor="middle")
        yy = 114
        for ln in wrap(sub, cw - 8, 13, k=0.48):
            s.text(x + cw / 2, yy, ln, size=13, fill=INK2, anchor="middle")
            yy += 16
    s.text(lx, 82, "Concept", size=16, weight="bold")
    s.text(lx, 101, "(numbered as in Fig. 1)", size=13, fill=INK2)

    y, rh, rg = 146, 70, 6
    for n, (concept, cells) in enumerate(LANES, 1):
        c = CONCEPT_COLORS[n - 1]
        s.rect(lx, y, cx0 - lx - 6, rh, stroke="none", fill=tint(c, 0.12), rx=6)
        cbadge(s, lx + 18, y + rh / 2, n)
        lines = wrap(concept, lw - 48, 15, k=0.52)
        ty = y + rh / 2 + 5 - (len(lines) - 1) * 9.5
        for j, ln in enumerate(lines):
            s.text(lx + 36, ty + j * 19, ln, size=15, weight="bold", fill=c)
        for i, txt in enumerate(cells):
            x = cols[i]
            if txt is None:
                s.rect(x, y, cw, rh, stroke=LINE, fill=BG, rx=6, sw=1, dash="3,3")
                continue
            s.rect(x, y, cw, rh, stroke=c, fill=tint(c, 0.06), rx=6, sw=1.2)
            lines = wrap(txt, cw - 18, 14, k=0.51)
            ty = y + rh / 2 + 5 - (len(lines) - 1) * 8.5
            for j, ln in enumerate(lines):
                s.text(x + 9, ty + j * 17, ln, size=14)
        y += rh + rg

    # researcher lane
    y += 6
    s.rect(lx, y, cx0 - lx - 6, rh, stroke=ORANGE, fill=BG, rx=6, sw=1.5, dash="6,4")
    for j, ln in enumerate(["Researcher", "in control"]):
        s.text(lx + 14, y + 30 + j * 19, ln, size=15, weight="bold", fill=ORANGE)
    for i, txt in enumerate(RESEARCHER):
        x = cols[i]
        s.rect(x, y, cw, rh, stroke=ORANGE, fill=BG, rx=6, sw=1.5, dash="6,4")
        lines = wrap(txt, cw - 18, 14, k=0.51)
        ty = y + rh / 2 + 5 - (len(lines) - 1) * 8.5
        for j, ln in enumerate(lines):
            s.text(x + 9, ty + j * 17, ln, size=14)
    s.save("fig2b_concepts_workflow.svg")


# ---------------------------------------------------------------- Figure 2c
# Simplified flow + WHY each stage serves the goal (own terms, not Fig 1's numbering).
WHY = [  # (span of boxes, heading, body)
    (("q", "kg"), "Grounded scope",
     "the question is sized to what the KG actually holds, not to memory"),
    (("fr",), "Hit and miss defined first",
     "a validation set must score and an expected-negative must not, so a null result "
     "stays interpretable"),
    (("rv",), "Fresh eyes",
     "a critic who did not write the plan, then the researcher"),
    (("me",), "Method proven", "tested on toy data before real data"),
    (("an",), "Checked first", "a cold reader re-counts the data before anyone sees it"),
    (("ev",), "Meaning last", "interpretive claims only once the evidence is in"),
]


def figure2c():
    s = SVG(960, 396)
    B = {"q": (12, 88, "Question", ["locked"]),
         "kg": (114, 104, "KG entries", ["from the KG"]),
         "fr": (232, 196, "Framing", ["hypothesis", "statistics plan", "validation set",
                                       "expected-negative"]),
         "rv": (442, 112, "Review", ["critic, then", "researcher"]),
         "me": (590, 110, "methods", ["build + test"]),
         "an": (714, 110, "analysis", ["run it"]),
         "ev": (838, 110, "evaluation", ["interpret,", "write paper"])}
    top, bh = 40, 112
    s.rect(4, 6, 560, 154, stroke="none", fill="#f5f5f3", rx=10)
    s.rect(582, 6, 374, 154, stroke="none", fill="#f5f5f3", rx=10)
    s.text(14, 28, "PLAN", size=15, weight="bold", fill=INK2)
    s.text(592, 28, "RUN", size=15, weight="bold", fill=INK2)
    for k, (x, w, title, lines) in B.items():
        s.rect(x, top, w, bh, stroke=INK, fill=BG, sw=1.6)
        s.text(x + w / 2, top + 26, title, size=16, weight="bold", anchor="middle")
        for j, ln in enumerate(lines):
            s.text(x + w / 2, top + 48 + j * 18, ln, size=14,
                   fill=INK if k == "fr" else INK2, anchor="middle")
    for u, v in [("q", "kg"), ("kg", "fr"), ("fr", "rv"), ("me", "an"), ("an", "ev")]:
        x1 = B[u][0] + B[u][1]
        s.arrow([(x1 + 1, top + bh / 2), (B[v][0] - 1, top + bh / 2)], INK2, sw=2)
    s.arrow([(555, top + bh / 2), (588, top + bh / 2)], INK, sw=2.4)

    # the lock, and why it matters
    s.rect(330, 170, 486, 28, stroke="none", fill=INK, rx=14)
    s.text(573, 189, "proposal locked: the framing cannot drift to fit the results",
           size=14, weight="bold", fill="#fff", anchor="middle")

    # why-cards, aligned under their stages
    cy, ch = 212, 124
    for keys, head, body in WHY:
        x = B[keys[0]][0]
        w = B[keys[-1]][0] + B[keys[-1]][1] - x
        s.rect(x, cy, w, ch, stroke=BLUE, fill=tint(BLUE, 0.07), sw=1.3)
        hl = wrap(head, w - 16, 15, k=0.55)
        yy = cy + 22
        for ln in hl:
            s.text(x + 8, yy, ln, size=15, weight="bold", fill=BLUE)
            yy += 18
        for ln in wrap(body, w - 16, 13, k=0.5):
            s.text(x + 8, yy + 2, ln, size=13)
            yy += 16

    # approvals + corrections
    y = 344
    xl, xr = B["fr"][0] + 98, B["ev"][0] + 55
    s.arrow([(xr, y), (xr, y + 32), (xl, y + 32), (xl, y + 2)], INK2, sw=1.8)
    s.text((xl + xr) / 2, y + 22, "each step approved by the researcher and committed; "
           "corrections loop back openly", size=13, fill=INK2, anchor="middle", style="italic")
    s.save("fig2c_flow_concepts.svg")


# ---------------------------------------------------------------- Figure 2d
# One row: each workflow step is labelled by the concept it carries.
STEPS_2D = [  # (key, width, step label, concept, how, examples); tuple example = (term, gloss)
    ("kg", 128, "SCOPE", "Grounded", "from the KG, not memory",
     ["experiments and publications listed by query", "genes resolved to locus tags",
      "KG gaps flagged, not filled"]),
    ("fr", 196, "FRAMING", "Pre-registered", "hit and miss set in advance",
     [("Hypothesis", "stated in prose"),
      ("Statistics plan", "the test and thresholds, or a reasoned “none”"),
      ("Validation set", "named genes and the behavior expected if it works"),
      ("Expected-negative", "a class that must not score"),
      ("Design comparability", "what each arm is compared against")]),
    ("rv", 124, "REVIEW", "Fresh eyes", "critic, then researcher",
     ["critic reads the plan cold", "researcher's design review", "delta pass after "
      "each change"]),
    ("me", 124, "METHODS", "Tested first", "on toy data",
     ["hand-computed toy cases", "pilot against an independent key", "a random sample of every bin checked"]),
    ("an", 124, "ANALYSIS", "Checked", "a cold critic re-counts",
     ["every number re-checked against the data files", "“all” and “every” verified, "
      "not glanced", "coder reports facts; the main thread judges"]),
    ("ev", 124, "EVALUATION", "Claims last", "interpret only now",
     ["judged by the pre-set hit and miss",
      "a negative result reported with its limits, not dropped", "strong words allowed only here"]),
]


def figure2d():
    s = SVG(960, 560)
    gap, x = 14, 12
    xs = {}
    for k, w, *_ in STEPS_2D:
        if k == "me":
            x += 30                      # room for the lock between plan and run
        xs[k] = (x, w)
        x += w + gap
    plan_l, plan_r = xs["kg"][0], xs["rv"][0] + xs["rv"][1]
    run_l, run_r = xs["me"][0], xs["ev"][0] + xs["ev"][1]

    for (l, r, lab) in [(plan_l, plan_r, "PLAN"), (run_l, run_r, "RUN")]:
        s.add(f'<path d="M{l},34 L{l},26 L{r},26 L{r},34" fill="none" stroke="{INK2}" '
              f'stroke-width="1.5"/>')
        s.add(f'<rect x="{(l + r) / 2 - 30}" y="16" width="60" height="20" fill="{BG}"/>')
        s.text((l + r) / 2, 31, lab, size=15, weight="bold", fill=INK2, anchor="middle")

    top = 46
    bodies, hmax = [], 0
    for k, w, step, concept, how, ex in STEPS_2D:
        x0 = xs[k][0]
        start = len(s.parts)
        s.text(x0 + 10, top + 22, step, size=13, weight="bold", fill=INK2)
        s.text(x0 + 10, top + 50, concept, size=17, weight="bold", fill=BLUE)
        yy = top + 74
        for ln in wrap(how, w - 20, 14, k=0.5):
            s.text(x0 + 10, yy, ln, size=14, weight="bold")
            yy += 18
        yy = top + 74 + 2 * 18                     # align dividers across boxes
        s.add(f'<line x1="{x0 + 10}" y1="{yy - 4}" x2="{x0 + w - 10}" y2="{yy - 4}" '
              f'stroke="{tint(BLUE, 0.45)}" stroke-width="1"/>')
        yy += 16
        for e in ex:
            if isinstance(e, tuple):
                term, gloss = e
                s.text(x0 + 10, yy, term, size=13, weight="bold", fill=BLUE)
                yy += 16
                for ln in wrap(gloss, w - 20, 13, k=0.5):
                    s.text(x0 + 10, yy, ln, size=13)
                    yy += 16
            else:
                for j, ln in enumerate(wrap(e, w - 30, 13, k=0.5)):
                    if j == 0:
                        s.text(x0 + 10, yy, "•", size=13, fill=BLUE)
                    s.text(x0 + 20, yy, ln, size=13)
                    yy += 16
            yy += 6
        bodies.append((x0, w, s.parts[start:]))
        del s.parts[start:]
        hmax = max(hmax, yy - top)
    h = hmax + 2
    for x0, w, body in bodies:
        s.rect(x0, top, w, h, stroke=BLUE, fill=tint(BLUE, 0.06), sw=1.6)
        s.parts.extend(body)

    order = [k for k, *_ in STEPS_2D]
    ay = top + 62
    for a, b in zip(order, order[1:]):
        xa, xb = xs[a][0] + xs[a][1], xs[b][0]
        s.arrow([(xa + 1, ay), (xb - 1, ay)], INK if a == "rv" else INK2,
                sw=2.4 if a == "rv" else 2)
    lx = xs["rv"][0] + xs["rv"][1] + 22
    s.rect(lx - 12, top + 10, 24, h - 20, stroke="none", fill=INK, rx=12)
    s.add(f'<text x="{lx + 5}" y="{top + h / 2}" font-size="13" font-weight="bold" '
          f'fill="#fff" text-anchor="middle" transform="rotate(-90 {lx + 5} {top + h / 2})">'
          f'PROPOSAL LOCKED</text>')

    y = top + h + 18
    for lab, c in [("Researcher agrees each step's scope before, and approves it after",
                    ORANGE),
                   ("Every step scripted and committed; nothing amended or overwritten", INK)]:
        s.rect(plan_l, y, run_r - plan_l, 28, stroke="none", fill=c, rx=14)
        s.text((plan_l + run_r) / 2, y + 19, lab, size=14, weight="bold", fill="#fff",
               anchor="middle")
        y += 38
    s.text((plan_l + run_r) / 2, y + 12, "Corrections loop back openly; the locked framing "
           "changes only by a recorded reopen.", size=13, fill=INK2, anchor="middle",
           style="italic")
    s.h = int(y + 26)
    s.save("fig2d_concepts_in_flow.svg")


# ---------------------------------------------------------------- Figure 2e
# Same content as 2d, laid out as a PLAN row and a RUN row (wider boxes, less wrapping).
def _concept_box(s, x0, top, w, step, concept, how, ex):
    """Draw box content; return (parts, height). Caller draws the frame behind it."""
    start = len(s.parts)
    s.text(x0 + 12, top + 22, step, size=13, weight="bold", fill=INK2)
    s.text(x0 + 12, top + 48, concept, size=18, weight="bold", fill=BLUE)
    s.text(x0 + 12, top + 70, how, size=14, weight="bold")
    s.add(f'<line x1="{x0 + 12}" y1="{top + 82}" x2="{x0 + w - 12}" y2="{top + 82}" '
          f'stroke="{tint(BLUE, 0.45)}" stroke-width="1"/>')
    yy = top + 102
    for e in ex:
        if isinstance(e, tuple):
            term, gloss = e
            lines = wrap(term + " — " + gloss, w - 24, 14, k=0.46)
            first = lines[0][len(term):]
            s.add(f'<text x="{x0 + 12}" y="{yy}" font-size="14" fill="{INK}">'
                  f'<tspan font-weight="bold" fill="{BLUE}">{escape(term)}</tspan>'
                  f'{escape(first)}</text>')
            yy += 18
            for ln in lines[1:]:
                s.text(x0 + 12, yy, ln, size=14)
                yy += 18
        else:
            for j, ln in enumerate(wrap(e, w - 34, 14, k=0.46)):
                if j == 0:
                    s.text(x0 + 12, yy, "•", size=14, fill=BLUE)
                s.text(x0 + 24, yy, ln, size=14)
                yy += 18
        yy += 5
    parts = s.parts[start:]
    del s.parts[start:]
    return parts, yy - top - 4


def figure2e():
    s = SVG(960, 700)
    steps = {k: (step, concept, how, ex) for k, _w, step, concept, how, ex in STEPS_2D}
    L, R, gap = 50, 948, 30
    rows = [("PLAN", [("kg", 240), ("fr", 356), ("rv", 242)]),
            ("RUN", [("me", 279), ("an", 280), ("ev", 279)])]
    y = 12
    geo = {}
    for ri, (lab, boxes) in enumerate(rows):
        x, drawn, hmax = L, [], 0
        for k, w in boxes:
            parts, h = _concept_box(s, x, y, w, *steps[k])
            drawn.append((k, x, w, parts))
            hmax = max(hmax, h)
            x += w + gap
        for k, x0, w, parts in drawn:
            s.rect(x0, y, w, hmax, stroke=BLUE, fill=tint(BLUE, 0.06), sw=1.6)
            s.parts.extend(parts)
            geo[k] = (x0, y, w, hmax)
        for (k1, x1, w1, _), (k2, x2, _w2, _) in zip(drawn, drawn[1:]):
            s.arrow([(x1 + w1 + 3, y + 44), (x2 - 3, y + 44)], INK, sw=3.2)
        # row label, rotated, in the left gutter
        cy = y + hmax / 2
        s.rect(12, y, 26, hmax, stroke="none", fill="#ececea", rx=8)
        s.add(f'<text x="{25 + 5}" y="{cy}" font-size="15" font-weight="bold" fill="{INK2}" '
              f'text-anchor="middle" transform="rotate(-90 30 {cy})">{lab}</text>')
        y += hmax
        if ri == 0:
            # lock between the rows
            rx, ry, rw, rh = geo["rv"]
            s.arrow([(rx + rw / 2, y + 2), (rx + rw / 2, y + 15)], INK, sw=3.2)
            s.rect(L, y + 16, R - L, 28, stroke="none", fill=INK, rx=14)
            s.text((L + R) / 2, y + 35, "PROPOSAL LOCKED — the framing cannot drift to fit "
                   "the results", size=14, weight="bold", fill="#fff", anchor="middle")
            s.arrow([(L + 140, y + 45), (L + 140, y + 58)], INK, sw=3.2)
            y += 60

    y += 16
    for lab, c in [("Researcher agrees each step's scope before, and approves it after",
                    ORANGE),
                   ("Every step scripted and committed; nothing amended or overwritten", INK)]:
        s.rect(12, y, R - 12, 28, stroke="none", fill=c, rx=14)
        s.text((12 + R) / 2, y + 19, lab, size=14, weight="bold", fill="#fff", anchor="middle")
        y += 38
    s.text((12 + R) / 2, y + 12, "Corrections loop back openly; the locked framing changes "
           "only by a recorded reopen.", size=13, fill=INK2, anchor="middle", style="italic")
    s.h = int(y + 26)
    s.save("fig2e_concepts_two_rows.svg")


# ---------------------------------------------------------------- Figure 3
def figure3():
    """Multi-agent design: who may do what (sources: .claude/agents/*.md, Rule 8)."""
    s = SVG(960, 452)

    def box(x, y, w, h, title, sub, bullets, c, tc=None):
        s.rect(x, y, w, h, stroke=c, fill=tint(c, 0.08), sw=2)
        s.text(x + 12, y + 26, title, size=17, weight="bold", fill=tc or c)
        yy = y + 46
        if sub:
            yy = s.para(x + 12, yy, sub, w - 24, size=13, fill=INK2) + 6
        for b in bullets:
            for k, ln in enumerate(wrap(b, w - 30, 14, k=0.46)):
                s.text(x + 12, yy, "•" if k == 0 else "", size=14)
                s.text(x + 24, yy, ln, size=14)
                yy += 19
            yy += 4

    box(12, 140, 124, 130, "Researcher", "owns the question", ["agrees scope", "approves"],
        ORANGE)
    box(186, 20, 200, 380, "Main thread", "Claude + research-methodology skill",
        ["owns all judgment", "reads the real data files", "writes notebook and paper",
         "commits each round", "only voice to the researcher"], INK2, INK)
    box(526, 20, 236, 180, "kg-coder", "coding subagent",
        ["kept alive across a milestone", "preloads the domain rules",
         "writes scripts, data, figures", "never interprets or commits"], AQUA, AQUA_TXT)
    box(526, 220, 236, 180, "critic", "reviewing subagent",
        ["fresh context every pass", "read-only: cannot edit",
         "sees only this milestone", "lens matched to the work"], VIOLET)

    # shared workspace
    s.rect(822, 20, 126, 380, stroke=LINE, fill="#f5f5f3")
    s.text(885, 46, "Shared", size=15, weight="bold", fill=INK2, anchor="middle")
    s.rect(834, 64, 102, 134, stroke=INK2, fill=BG)
    for j, ln in enumerate(["Files", "+ git"]):
        s.text(885, 100 + j * 20, ln, size=16 if j == 0 else 14, weight="bold" if j == 0
               else "normal", anchor="middle")
    for j, ln in enumerate(["every round", "committed"]):
        s.text(885, 150 + j * 17, ln, size=13, fill=INK2, anchor="middle")
    s.rect(834, 222, 102, 164, stroke=BLUE, fill=tint(BLUE, 0.08))
    for j, ln in enumerate(["Knowledge", "graph"]):
        s.text(885, 258 + j * 20, ln, size=16, weight="bold", fill=BLUE, anchor="middle")
    for j, ln in enumerate(["sole data", "source; MCP +", "Python API"]):
        s.text(885, 316 + j * 17, ln, size=13, fill=INK2, anchor="middle")

    # researcher <-> main
    s.arrow([(138, 205), (184, 205)], ORANGE, both=True, sw=2)
    s.text(161, 195, "gates", size=13, fill=ORANGE, anchor="middle")

    # main <-> subagents
    s.arrow([(388, 82), (524, 82)], INK2, sw=2)
    s.text(456, 74, "task", size=14, fill=INK2, anchor="middle")
    s.arrow([(524, 138), (388, 138)], AQUA_TXT, sw=2)
    s.text(456, 130, "run-manifest:", size=13, fill=AQUA_TXT, anchor="middle")
    s.text(456, 160, "facts, not", size=13, fill=AQUA_TXT, anchor="middle")
    s.text(456, 176, "conclusions", size=13, fill=AQUA_TXT, anchor="middle")
    s.arrow([(388, 282), (524, 282)], INK2, sw=2)
    s.text(456, 274, "scope + lens", size=14, fill=INK2, anchor="middle")
    s.arrow([(524, 338), (388, 338)], VIOLET, sw=2)
    s.text(456, 330, "findings", size=13, fill=VIOLET, anchor="middle")
    s.text(456, 360, "each one", size=13, fill=VIOLET, anchor="middle")
    s.text(456, 376, "dispositioned", size=13, fill=VIOLET, anchor="middle")

    # subagents -> shared
    s.arrow([(764, 110), (820, 110)], AQUA_TXT, sw=2, both=True)
    s.text(792, 96, "writes,", size=13, fill=AQUA_TXT, anchor="middle")
    s.text(792, 132, "queries", size=13, fill=AQUA_TXT, anchor="middle")
    s.arrow([(764, 310), (820, 310)], VIOLET, sw=2)
    s.text(792, 296, "reads,", size=13, fill=VIOLET, anchor="middle")
    s.text(792, 332, "checks", size=13, fill=VIOLET, anchor="middle")

    s.rect(12, 414, 936, 32, stroke="none", fill=tint(INK2, 0.1), rx=16)
    s.text(480, 435, "Doing and judging are split: the coder cannot conclude, the critic cannot "
           "edit, and only the main thread speaks to the researcher.", size=14, weight="bold",
           anchor="middle")
    s.save("fig3_agents.svg")


if __name__ == "__main__":
    figure1()
    figure2()
    figure2b()
    figure2c()
    figure2d()
    figure2e()
    figure3()
