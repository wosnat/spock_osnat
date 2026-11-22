"""Generate the Spock paper schematics as SVG (then render_figures.sh -> PNG/PDF).

Sized for HALF AN A4 PAGE: canvas 960 units wide, printed at 170 mm text width
(1 unit ~ 0.177 mm). Font floor 13 units (~6.5 pt); body 14-16 (~7-8 pt).

Fig 1  fig1_concepts_cards.svg - six safeguard cards (danger, verbatim quote, how).
Fig 2  fig2_process_safeguards.svg - the process (Plan -> Run) with each AI step drawn as the
                           Figure 1 card it carries; B = what "Pre-register the test" fixes.
Fig S1 figS1_agents.svg   - supplementary: which AI may do what (.claude/agents/).

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
ORANGE_TXT = "#b4461a"  # orange darkened for text on its tint
MAGENTA, OCHRE = "#b0397a", "#8a6200"  # Fig 1 concepts 5-6 (no role meaning)
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
        self.colors = {INK, INK2, BLUE, ORANGE, AQUA, AQUA_TXT, VIOLET, RED, MAGENTA, OCHRE,
                       SLATE, TEAL}

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
            f'fill="{c}"/></marker>' for c in sorted(self.colors))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}"><defs>{markers}</defs>'
               f'<rect width="100%" height="100%" fill="{BG}"/>' + "\n".join(self.parts) + "</svg>")
        (OUT / name).write_text(svg, encoding="utf-8")
        print("wrote", OUT / name)


CONCEPT_COLORS = [BLUE, ORANGE, AQUA_TXT, VIOLET, MAGENTA, OCHRE]   # Fig 1 rows 1-6
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
     "The knowledge graph (KG) is the sole data source", BLUE,
     "Every claim must trace to a KG query. Never rely on intrinsic knowledge for data.",
     "Each finding is tagged: from the KG, interpretation, or a gap in the KG"),
    ("Confirming the hoped-for result",
     "success criteria chosen after the data are seen",
     "Pre-registered framing, locked before data", ORANGE,
     "…a pre-registered expected-negative — a class that should not score if the signal is "
     "genuine.",
     "Also fixed in advance: the statistical test and genes of known expected behavior"),
    ("Narrated, not measured",
     "the agent's own summary is trusted; its output files are never opened",
     "Execution separated from judgment", AQUA_TXT,
     "You execute; the main [agent] judges. You return artifacts, not conclusions.",
     "A coding sub-agent runs the scripts; the main agent judges from the output files"),
    ("Grading one's own story",
     "the author cannot see the holes in their own narrative",
     "Independent fresh-context critic", VIOLET,
     "The author who wrote the story cannot reliably see its holes; a fresh reader of the "
     "data files can.",
     "A separate agent, new to the analysis, must clear each result before the researcher sees it"),
    ("Overclaiming",
     "the language outruns the evidence",
     "Describe before interpreting", MAGENTA,
     "Words like “all”, “every”, “systematically” … require a query against the data file, "
     "not a heatmap glance.",
     "Evaluative words such as “striking” are held back until the final evaluation step"),
    ("Untraceable results",
     "arithmetic in chat; analyses silently revised",
     "Scripts and a complete history", OCHRE,
     "Chat-computed statistics are unreproducible — they can't be rerun, verified, or shared.",
     "All computation in saved scripts; every iteration committed to git, never rewritten"),
]


def figure1():
    s = SVG(960, 694)
    xr, wr = 12, 300          # risk column
    xc, wc = 352, 596         # concept column
    s.text(xr + 4, 28, "Threat to validity", size=16, weight="bold", fill=RED)
    s.text(xc + 4, 28, "Spock safeguard — quoted from its instructions to the AI", size=16, weight="bold")

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
        yy = s.para(xc + 16, y + 47, f"“{quote}”", wc - 30, size=14, style="italic")
        s.text(xc + 16, yy + 1, src, size=13, fill=INK2)
        y += rh + gap

    s.rect(xr, y + 4, xc + wc - xr, 38, stroke=ORANGE, fill=tint(ORANGE, 0.08), rx=19)
    s.text((xr + xc + wc) / 2, y + 28, "Throughout: the researcher agrees each step's scope "
           "and approves it; the assistant never closes a step alone.",
           size=14, weight="bold", fill=INK, anchor="middle")
    s.save("drafts/fig1_concepts.svg")


# ---------------------------------------------------------------- Figure 1b
# Same safeguards as Figure 1; the left column is framed unmistakably as failure modes
# (red header band, warning icon, threats phrased as what goes wrong).
PROBLEMS = [
    ("AI states facts from memory",
     "gene names, values and experiments are recalled, not queried, and may be wrong"),
    ("Criteria fitted to the result",
     "success is defined after seeing the data, so any outcome can pass"),
    ("Unchecked summaries",
     "the AI's own summary is trusted; its output files are never opened"),
    ("Self-grading",
     "the AI that wrote the story also checks it, and misses its holes"),
    ("Overclaiming",
     "the wording outruns the evidence"),
    ("Untraceable results",
     "numbers computed in chat; analyses silently revised"),
]
RED_TXT = "#b3261e"  # red darkened for text on a light tint


def warn_icon(s, x, y):
    """Red warning triangle, top-left corner at (x, y), 22 wide."""
    s.add(f'<polygon points="{x + 11},{y} {x + 22},{y + 19} {x},{y + 19}" fill="{RED}"/>')
    s.text(x + 11, y + 16.5, "!", size=13, weight="bold", fill="#fff", anchor="middle")


SLATE, TEAL = "#4a5a6c", "#0b7f99"
# Fig 1b safeguard colours: nothing red-adjacent (red is reserved for the problem column).
COLORS_1B = [BLUE, SLATE, AQUA_TXT, VIOLET, TEAL, OCHRE]


def icon(s, kind, x, y, c):
    """24x24 line icon in colour c, top-left at (x, y)."""
    g = f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "database":      # the KG
        s.add(f'<g {g}><ellipse cx="{x + 12}" cy="{y + 5}" rx="9" ry="3.5"/>'
              f'<path d="M{x + 3},{y + 5} V{y + 19} a9,3.5 0 0 0 18,0 V{y + 5}"/>'
              f'<path d="M{x + 3},{y + 12} a9,3.5 0 0 0 18,0"/></g>')
    elif kind == "lock":        # locked framing
        s.add(f'<g {g}><path d="M{x + 7},{y + 11} V{y + 7} a5,5 0 0 1 10,0 V{y + 11}"/></g>'
              f'<rect x="{x + 4}" y="{y + 11}" width="16" height="12" rx="2" fill="{c}"/>')
    elif kind == "scales":      # judgment kept apart
        s.add(f'<g {g}><path d="M{x + 12},{y + 3} V{y + 22} M{x + 7},{y + 22} H{x + 17} '
              f'M{x + 3},{y + 6} H{x + 21} M{x + 3},{y + 6} L{x},{y + 14} M{x + 3},{y + 6} '
              f'L{x + 6},{y + 14} M{x + 21},{y + 6} L{x + 18},{y + 14} M{x + 21},{y + 6} '
              f'L{x + 24},{y + 14}"/>'
              f'<path d="M{x},{y + 14} a3,2.5 0 0 0 6,0 Z M{x + 18},{y + 14} a3,2.5 0 0 0 6,0 Z" '
              f'fill="{c}"/></g>')
    elif kind == "magnifier":   # fresh reader
        s.add(f'<g {g}><circle cx="{x + 10}" cy="{y + 10}" r="7"/>'
              f'<path d="M{x + 15},{y + 15} L{x + 22},{y + 22}" stroke-width="3"/></g>')
    elif kind == "bars":        # describe the data first
        s.add(f'<g fill="{c}"><rect x="{x + 3}" y="{y + 13}" width="4.5" height="8"/>'
              f'<rect x="{x + 10}" y="{y + 7}" width="4.5" height="14"/>'
              f'<rect x="{x + 17}" y="{y + 2}" width="4.5" height="19"/></g>'
              f'<path d="M{x + 1},{y + 22.5} H{x + 23}" {g}/>')
    elif kind == "check":       # verified
        s.add(f'<g {g}><circle cx="{x + 12}" cy="{y + 12}" r="10"/>'
              f'<path d="M{x + 7},{y + 12.5} L{x + 10.5},{y + 16} L{x + 17},{y + 8.5}"/></g>')
    elif kind == "code":        # everything in scripts
        s.add(f'<path d="M{x + 7},{y + 6} L{x + 1},{y + 12} L{x + 7},{y + 18} '
              f'M{x + 17},{y + 6} L{x + 23},{y + 12} L{x + 17},{y + 18} '
              f'M{x + 14},{y + 3} L{x + 10},{y + 21}" {g}/>')


ICONS_1B = ["database", "lock", "scales", "magnifier", "bars", "code"]


# ---------------------------------------------------------------- Figure 1 (cards)
# The new Figure 1: six safeguards in research-stage order. Quotes are verbatim from
# .claude/ (checked by check_quotes.py; [brackets] = editorial insertion, … = elision).
# No card is red: red is reserved for the danger line. Orange is the frame (researcher).
CARDS = [
    dict(stage="Plan", title="Look it up", danger="guessing",
         gloss="facts recalled, not looked up",
         quote="Every claim traces to a KG query. Never take data from memory.",
         source="skills/research-methodology/SKILL.md",
         how="Each finding is tagged: from the KG, interpretation, or a gap.",
         icon="kg_lookup", color=BLUE),
    dict(stage="Plan", title="Scope first", danger="the plan outruns the data",
         gloss="criteria set for data that can't deliver them",
         quote="… a throwaway test … of what the data and annotations can actually tell apart.",
         source="skills/research-methodology/references/plan-phase.md",
         how="Data, annotations and controls are checked before the criteria are set.",
         icon="bars", color=TEAL),
    dict(stage="Plan", title="Pre-register the test", danger="a test that can't fail",
         gloss="any outcome can pass",
         quote="Without both kinds [positive and negative controls], a true null and a blind method "
               "look the same.",
         source="skills/research-methodology/references/plan-phase.md",
         how="Controls and decision rule fixed before the answer is seen (Fig. 2B).",
         icon="clipboard_lock", color=SLATE),
    dict(stage="Run", title="Check the computation",
         danger="silent errors",
         gloss="tests pass, real data breaks it",
         quote="Toy tests catch logic errors; only an independent path catches wrong calls, "
               "defaults, filters and paging.",
         source="skills/research-methodology/references/research-notebook.md",
         how="Toy data, an independent answer and a code review; correct background and "
             "multiple-testing correction.",
         icon="flask_check", color=AQUA_TXT),
    dict(stage="Run", title="Claims match evidence", danger="narrative fabrication",
         gloss="the wording outruns the evidence",
         quote="[Words like] ‘every’, ‘none’ … need a query against the data file, "
               "not a glance at a heatmap.",
         source="skills/research-methodology/SKILL.md",
         how="Numbers first, interpretation after; each finding set against other KG studies.",
         icon="scales", color=OCHRE),
    dict(stage="Run", title="Separate the roles", danger="grading your own work",
         gloss="the author misses their own holes",
         quote="You execute; the main thread judges. You return artifacts, not conclusions.",
         source="agents/kg-coder.md",
         how="One AI runs the code, another judges the output, a third, new to the work, "
             "reviews.",
         icon="roles", color=VIOLET),
]


# Figure 2B: what "Pre-register the test" fixes. The skill's Framing headings, each with a few
# verbatim words (checked by check_quotes.py against FRAMING_SOURCE; … = elision).
FRAMING_SOURCE = "skills/research-methodology/references/plan-phase.md"
FRAMING = [
    ("Hypothesis", "in prose"),
    ("Approach", "how, and why"),
    ("Statistics plan", "test(s) and thresholds"),
    ("Positive controls", "must show the expected effect"),
    ("Negative controls", "should not score"),
    ("Decision rule", "every reading … named in advance"),
    ("Design comparability", "what each arm is compared against"),
]
FRAMING_FOOTER = "controls pass → method frozen → targets scored once, last."

def icon_cards(s, kind, x, y, c):
    """24x24 icons for the Figure 1 cards; falls back to icon() for the shared kinds."""
    g = f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "kg_lookup":       # database + magnifier: look it up in the KG
        s.add(f'<g {g}><ellipse cx="{x + 9}" cy="{y + 5}" rx="7.5" ry="3"/>'
              f'<path d="M{x + 1.5},{y + 5} V{y + 18} a7.5,3 0 0 0 9,2.9"/>'
              f'<path d="M{x + 16.5},{y + 5} V{y + 9}"/>'
              f'<path d="M{x + 1.5},{y + 11.5} a7.5,3 0 0 0 9,2.9"/></g>'
              f'<circle cx="{x + 16}" cy="{y + 15}" r="5" fill="#fff" stroke="{c}" '
              f'stroke-width="2"/>'
              f'<path d="M{x + 19.5},{y + 18.5} L{x + 23.5},{y + 22.5}" fill="none" '
              f'stroke="{c}" stroke-width="3" stroke-linecap="round"/>')
    elif kind == "clipboard_lock":  # the plan, locked
        s.add(f'<g {g}><rect x="{x + 3}" y="{y + 3}" width="16" height="20" rx="2"/>'
              f'<rect x="{x + 7}" y="{y + 1}" width="8" height="4" rx="1" fill="#fff"/>'
              f'<path d="M{x + 7},{y + 10} H{x + 15} M{x + 7},{y + 14} H{x + 11}"/>'
              f'<path d="M{x + 16},{y + 15} V{y + 13} a3,3 0 0 1 6,0 V{y + 15}" fill="#fff"/></g>'
              f'<rect x="{x + 14}" y="{y + 15}" width="10" height="8" rx="1.5" fill="{c}"/>')
    elif kind == "flask_check":     # the computation, checked
        s.add(f'<g {g}><path d="M{x + 6},{y + 2} H{x + 14} M{x + 8},{y + 2} V{y + 9} '
              f'L{x + 2},{y + 21} a1.5,1.5 0 0 0 1.4,2 H{x + 12} M{x + 12},{y + 2} V{y + 9} '
              f'L{x + 14},{y + 13}"/></g>'
              f'<circle cx="{x + 18}" cy="{y + 18}" r="6" fill="{c}"/>'
              f'<path d="M{x + 15},{y + 18} L{x + 17.2},{y + 20.2} L{x + 21},{y + 15.8}" '
              f'fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" '
              f'stroke-linejoin="round"/>')
    elif kind == "roles":           # three figures: runs, judges, reviews
        for cx in (x + 4, x + 12, x + 20):
            s.add(f'<g {g}><circle cx="{cx}" cy="{y + 8}" r="3"/>'
                  f'<path d="M{cx - 4},{y + 21} V{y + 17} a4,4 0 0 1 8,0 V{y + 21}"/></g>')
    else:
        icon(s, kind, x, y, c)


def _card_layout(card, variant, w):
    """Text blocks and total height of one card; w = card width."""
    inner = w - 32
    danger = f"against: {card['danger']}" + (f" — {card['gloss']}" if variant == "b" else "")
    blocks = dict(
        # k: average glyph width / size, measured on the render (regular 0.45, italic 0.48)
        danger=wrap(danger, inner, 13, k=0.46),
        quote=wrap(f"“{card['quote']}”", inner, 14, k=0.5),
        how=wrap(card["how"], inner, 13, k=0.46),
    )
    h = (20 + 24                                   # stage tag, title
         + 20 + len(blocks["danger"]) * 13 * 1.28  # danger line(s)
         + 6 + len(blocks["quote"]) * 14 * 1.28    # quote
         + 12 + len(blocks["how"]) * 13 * 1.28     # rule + how line(s)
         + 8)
    return blocks, h


def figure1_cards(variant):
    """New Figure 1: six safeguard cards (3 x 2) inside the researcher's frame.
    variant 'a' = terse danger line (chosen); 'b' = danger line with a gloss (not rendered)."""
    W, fx, fw = 960, 12, 936            # canvas; frame x and width
    cols, gap, pad = 3, 12, 16
    cw = (fw - 2 * pad - (cols - 1) * gap) / cols
    fy = 22                             # frame top (labels sit on it)
    rows = [CARDS[i:i + cols] for i in range(0, len(CARDS), cols)]
    lays = [[_card_layout(c, variant, cw) for c in row] for row in rows]
    rh = [max(h for _, h in row) for row in lays]
    H = fy + 26 + sum(rh) + gap * (len(rows) - 1) + 26 + 22
    s = SVG(W, round(H))

    fh = H - fy - 22
    s.rect(fx, fy, fw, fh, stroke=ORANGE, fill=BG, rx=18, sw=2.5)

    def pill(x, y, txt, anchor):
        tw = len(txt) * 14 * 0.52 + 24
        x0 = x if anchor == "start" else x - tw
        s.rect(x0, y - 13, tw, 26, stroke=ORANGE, fill=tint(ORANGE, 0.14), rx=13, sw=1.5)
        s.text(x0 + tw / 2, y + 5, txt, size=14, weight="bold", anchor="middle")

    pill(fx + 22, fy, "The researcher approves every step; the AI never moves on alone", "start")
    pill(fx + fw - 22, fy + fh, "Everything is on the record", "end")
    note = "quotes: Spock’s instructions to the AI"
    nw = len(note) * 13 * 0.5 + 14
    s.rect(fx + fw - 22 - nw, fy - 9, nw, 18, stroke="none", fill=BG, rx=0)
    s.text(fx + fw - 22 - nw / 2, fy + 4.5, note, size=13, fill=INK2, anchor="middle",
           style="italic")

    y = fy + 26
    for row, lay, h in zip(rows, lays, rh):
        for i, (card, (blocks, _)) in enumerate(zip(row, lay)):
            x, c = fx + pad + i * (cw + gap), card["color"]
            tx = x + 16
            # thick left edge that follows the rounded corners: colour, tint over it, outline
            s.rect(x, y, cw, h, stroke="none", fill=c)
            s.rect(x + 4, y, cw - 4, h, stroke="none", fill=tint(c, 0.06))
            s.rect(x, y, cw, h, stroke=c, fill="none", sw=1.5)
            assert MIN_FONT == 13      # stage tag sits at the font floor; lighter, not smaller
            s.add(f'<text x="{tx}" y="{y + 20}" font-size="13" letter-spacing="1.2" '
                  f'fill="{INK2}">{escape(card["stage"].upper())}</text>')
            k = 1.45                   # icons enlarged from their 24-unit grid
            s.add(f'<g transform="translate({x + cw - 14 - 24 * k},{y + 12}) scale({k})">')
            icon_cards(s, card["icon"], 0, 0, c)
            s.add('</g>')
            assert len(wrap(card["title"], cw - 32 - 24 * k - 6, 17)) == 1, card["title"]
            s.text(tx, y + 44, card["title"], size=17, weight="bold", fill=c)
            yy = y + 64
            for ln in blocks["danger"]:
                s.text(tx, yy, ln, size=13, fill=RED_TXT)
                yy += 13 * 1.28
            yy += 6
            for ln in blocks["quote"]:
                s.text(tx, yy, ln, size=14, style="italic")
                yy += 14 * 1.28
            s.add(f'<path d="M{tx},{yy - 6} H{x + cw - 16}" stroke="{tint(c, 0.4)}" '
                  f'stroke-width="1"/>')
            yy += 12
            for ln in blocks["how"]:
                s.text(tx, yy, ln, size=13, fill=INK)
                yy += 13 * 1.28
            assert yy - 13 * 1.28 + 8 <= y + h + 0.5, (card["title"], yy, y + h)
        y += h + gap

    s.save("fig1_concepts_cards.svg")


def figure1b():
    s = SVG(960, 706)
    xr, wr = 12, 300          # problem column
    xc, wc = 352, 596         # safeguard column
    s.rect(xr, 8, wr, 32, stroke="none", fill=RED, rx=6)
    s.text(xr + 14, 30, "What can go wrong", size=16, weight="bold", fill="#fff")
    s.rect(xc, 8, wc, 32, stroke="none", fill=INK, rx=6)
    s.text(xc + 16, 30, "How Spock prevents it", size=16, weight="bold", fill="#fff")
    s.text(xc + wc - 14, 30, "quoted from its instructions to the AI", size=13,
           fill="#e6e6e3", anchor="end", style="italic")

    y, rh, gap = 54, 92, 8
    for (prob, gloss), (_, _, concept, _, quote, src), c, ic in zip(
            PROBLEMS, ROWS, COLORS_1B, ICONS_1B):
        s.rect(xr, y, wr, rh, stroke=RED, fill=tint(RED, 0.08), sw=1.2, dash="5 3")
        warn_icon(s, xr + 12, y + 13)
        s.text(xr + 42, y + 29, prob, size=16, weight="bold", fill=RED_TXT)
        s.para(xr + 14, y + 54, gloss, wr - 26, size=14, fill=INK2)

        s.arrow([(xr + wr + 6, y + rh / 2), (xc - 8, y + rh / 2)], INK2, sw=2)

        s.rect(xc, y, wc, rh, stroke=c, fill=tint(c, 0.06), sw=1.5)
        s.add(f'<rect x="{xc}" y="{y}" width="4" height="{rh}" fill="{c}"/>')
        s.text(xc + 16, y + 25, concept, size=16, weight="bold", fill=c)
        icon(s, ic, xc + wc - 38, y + 10, c)
        yy = s.para(xc + 16, y + 47, f"“{quote}”", wc - 30, size=14, style="italic")
        s.text(xc + 16, yy + 1, src, size=13, fill=INK2)
        y += rh + gap

    s.rect(xr, y + 4, xc + wc - xr, 38, stroke=INK2, fill=tint(INK2, 0.08), rx=19)
    s.text((xr + xc + wc) / 2, y + 28, "Throughout: the researcher agrees each step's scope "
           "and approves it; the assistant never closes a step alone.",
           size=14, weight="bold", fill=INK, anchor="middle")
    s.save("drafts/fig1b_concepts.svg")


# ---------------------------------------------------------------- Figure 1c
# Six safeguards, ordered by research stage so the rows map onto Figure 2e.
# (stage, problem, gloss, safeguard, colour, icon, verbatim quote, how it is enforced)
# Quote sources: SKILL.md Rules 1, 5, 9 and the Plan framing; references/research-notebook.md
# (toy-data verification); references/step-protocol.md GATE C.
ROWS_1C = [
    ("PLAN", "AI states facts from memory",
     "gene names, values and experiments are recalled, not queried, and may be wrong",
     "Grounded in the knowledge graph (KG)", BLUE, "database",
     "Every claim must trace to a KG query. Never rely on intrinsic knowledge for data.",
     "Each finding is tagged by source; gaps in the KG are flagged, not filled"),
    ("PLAN", "Criteria fitted to the result",
     "success is defined after seeing the data, so any outcome can pass",
     "Pre-registered framing", SLATE, "lock",
     "The validation set says what a hit looks like; this [expected-negative] says what a "
     "miss looks like.",
     "Also fixed: the statistics plan · changed only by a recorded reopening · nulls reported"),
    ("METHOD", "Silent errors in the method",
     "the tests pass, yet the code is wrong on the real data files",
     "Methods verified before use", TEAL, "check",
     "Create small synthetic input, compute expected output by hand, run the utility, compare.",
     "Then a pilot against an independent answer key, and a random sample of every bin"),
    ("ANALYSIS", "Grading one's own work",
     "the AI that produced a result also judges it, and misses its holes",
     "Doing, judging and reviewing kept apart", VIOLET, "scales",
     "The author who wrote the story cannot reliably see its holes; a fresh reader of the "
     "data files can.",
     "A coding agent runs scripts, the main agent judges, a fresh-context critic reviews"),
    ("CLAIMS", "Overclaiming",
     "the wording outruns the evidence",
     "Verify before generalizing", AQUA_TXT, "magnifier",
     "Words like “all”, “every”, “systematically” … require a query against the data file, "
     "not a heatmap glance.",
     "Numbers and direction first; interpretive words wait for the evaluation step"),
    ("RECORD", "Untraceable results",
     "numbers computed in chat; earlier analyses silently overwritten",
     "Scripts and a complete history", OCHRE, "code",
     "Chat-computed statistics are unreproducible — they can't be rerun, verified, or shared.",
     "Every iteration is committed; wrong turns stay in the history, never rewritten"),
]


def figure1c():
    s = SVG(960, 722)
    xr, wr = 12, 300          # problem column
    xc, wc = 352, 596         # safeguard column
    s.rect(xr, 8, wr, 32, stroke="none", fill=RED, rx=6)
    s.text(xr + 14, 30, "What can go wrong", size=16, weight="bold", fill="#fff")
    s.rect(xc, 8, wc, 32, stroke="none", fill=INK, rx=6)
    s.text(xc + 16, 30, "How Spock prevents it", size=16, weight="bold", fill="#fff")
    s.text(xc + wc - 14, 30, "quoted from its instructions to the AI", size=13,
           fill="#e6e6e3", anchor="end", style="italic")

    y, rh, gap = 52, 96, 7
    for stage, prob, gloss, concept, c, ic, quote, how in ROWS_1C:
        s.rect(xr, y, wr, rh, stroke=RED, fill=tint(RED, 0.08), sw=1.2, dash="5 3")
        s.text(xr + 14, y + 19, stage, size=13, weight="bold", fill=INK2)
        warn_icon(s, xr + 12, y + 27)
        s.text(xr + 42, y + 43, prob, size=16, weight="bold", fill=RED_TXT)
        s.para(xr + 14, y + 66, gloss, wr - 26, size=14, fill=INK2)

        s.arrow([(xr + wr + 6, y + rh / 2), (xc - 8, y + rh / 2)], INK2, sw=2)

        s.rect(xc, y, wc, rh, stroke=c, fill=tint(c, 0.06), sw=1.5)
        s.add(f'<rect x="{xc}" y="{y}" width="4" height="{rh}" fill="{c}"/>')
        s.text(xc + 16, y + 25, concept, size=16, weight="bold", fill=c)
        icon(s, ic, xc + wc - 38, y + 10, c)
        yy = s.para(xc + 16, y + 48, f"“{quote}”", wc - 60, size=14, style="italic")
        s.text(xc + 16, yy + 3, how, size=13, fill=INK2)
        y += rh + gap

    s.rect(xr, y + 3, xc + wc - xr, 38, stroke=INK2, fill=tint(INK2, 0.08), rx=19)
    s.text((xr + xc + wc) / 2, y + 27, "Throughout: the researcher agrees each step's scope "
           "and approves it; the assistant never closes a step alone.",
           size=14, weight="bold", fill=INK, anchor="middle")
    s.save("drafts/fig1c_concepts.svg")


# ---------------------------------------------------------------- Figure 1e
# Figure 1c aligned with Figure 2h: safeguard names = the Fig 2h legend, stages = Fig 2h stages,
# plain-language enforcement lines, and the plainest verbatim quote from each rule
# (SKILL.md Rule 1; Plan step 4 "Check that the approach can work"; Two modes, control-validated
# order; research-notebook.md toy-data
# verification; step-protocol.md GATE C; Rule 9 "Describe before interpreting"; Rule 5).
ROWS_1E = [
    ("PLAN", "AI states facts from memory",
     "gene names, values and experiments are recalled rather than looked up",
     "KG data only", BLUE, "database",
     "Every claim must trace to a KG query. Never rely on intrinsic knowledge for data.",
     "Data come from the knowledge graph (KG); gaps are flagged, not filled"),
    ("PLAN", "Criteria fitted to the result",
     "success is defined after seeing the data, so any outcome can pass",
     "Criteria set first", SLATE, "lock",
     "controls pass → method frozen → targets scored once, last.",
     "Controls and decision rule fixed in the plan (Fig. 2B); anything seen earlier is exploratory"),
    ("PLAN", "Plan outruns the data",
     "success criteria are set for data or annotations that cannot deliver them",
     "Scope first", MAGENTA, "bars",
     "A quick, throwaway test … of what the data and annotations can actually tell apart.",
     "Data, annotations and controls are checked before the criteria are set"),
    ("BUILD METHOD", "Silent errors in the method",
     "the tests pass, yet the code is wrong on the real data",
     "Method tested", TEAL, "check",
     "Create small synthetic input, compute expected output by hand, run [the code], compare.",
     "Then checked against answers built independently, and on random samples of output"),
    ("ANALYSE", "Grading one's own work",
     "the AI that produced a result also judges it, and misses its holes",
     "Doing ≠ judging", VIOLET, "scales",
     "The author who wrote the story cannot reliably see its holes; a fresh reader of the "
     "data files can.",
     "One AI runs the code, another judges the output, a third, new to the work, reviews"),
    ("EVALUATE", "Overclaiming",
     "the wording outruns the evidence",
     "Claims checked", AQUA_TXT, "magnifier",
     "Numbers and direction first, interpretation second.",
     "Words such as “all” or “every” must be checked against the data first"),
    ("THROUGHOUT", "Untraceable results",
     "numbers computed in chat; earlier analyses silently overwritten",
     "Full history", OCHRE, "code",
     "Chat-computed statistics are unreproducible — they can't be rerun, verified, or shared.",
     "All computation in saved scripts; every version kept, never overwritten"),
]


def figure1e():
    s = SVG(960, 825)
    xr, wr = 12, 300
    xc, wc = 352, 596
    s.rect(xr, 8, wr, 32, stroke="none", fill=RED, rx=6)
    s.text(xr + 14, 30, "What can go wrong", size=16, weight="bold", fill="#fff")
    s.rect(xc, 8, wc, 32, stroke="none", fill=INK, rx=6)
    s.text(xc + 16, 30, "How Spock prevents it", size=16, weight="bold", fill="#fff")
    s.text(xc + wc - 14, 30, "quoted from its instructions to the AI", size=13,
           fill="#e6e6e3", anchor="end", style="italic")

    y, rh, gap = 52, 96, 7
    for stage, prob, gloss, concept, c, ic, quote, how in ROWS_1E:
        s.rect(xr, y, wr, rh, stroke=RED, fill=tint(RED, 0.08), sw=1.2, dash="5 3")
        s.text(xr + 14, y + 19, stage, size=13, weight="bold", fill=INK2)
        warn_icon(s, xr + 12, y + 27)
        s.text(xr + 42, y + 43, prob, size=16, weight="bold", fill=RED_TXT)
        s.para(xr + 14, y + 66, gloss, wr - 26, size=14, fill=INK)

        s.arrow([(xr + wr + 6, y + rh / 2), (xc - 8, y + rh / 2)], INK2, sw=2)

        s.rect(xc, y, wc, rh, stroke=c, fill=tint(c, 0.06), sw=1.5)
        s.add(f'<rect x="{xc}" y="{y}" width="4" height="{rh}" fill="{c}"/>')
        s.text(xc + 16, y + 25, concept, size=16, weight="bold", fill=c)
        icon(s, ic, xc + wc - 38, y + 10, c)
        yy = s.para(xc + 16, y + 48, f"“{quote}”", wc - 60, size=14, style="italic")
        s.text(xc + 16, yy + 3, how, size=13, fill=INK)
        y += rh + gap

    s.rect(xr, y + 3, xc + wc - xr, 38, stroke=INK2, fill=tint(INK2, 0.08), rx=19)
    s.text((xr + xc + wc) / 2, y + 27, "Throughout: the researcher approves every plan and "
           "every stage; the AI never moves on alone.",
           size=14, weight="bold", fill=INK, anchor="middle")
    s.save("drafts/fig1e_concepts.svg")


# ---------------------------------------------------------------- Figure 2f
COLORS_1C = dict((r[5], r[4]) for r in ROWS_1C)   # icon kind -> safeguard colour (Fig 1c)


def icon_badge(s, kind, cx, cy, r=11, c=None):
    """Fig 1c safeguard icon in a white disc ringed in its colour."""
    c = c or COLORS_1C[kind]
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{c}" stroke-width="1.8"/>')
    k = (r * 1.35) / 24
    s.add(f'<g transform="translate({cx - 12 * k},{cy - 12 * k}) scale({k})">')
    icon(s, kind, 0, 0, c)
    s.add("</g>")


def figure2f():
    """The research process as a swimlane flowchart: one lane per actor, the Plan, the lock,
    and one Run milestone expanded (methods, analysis and evaluation each repeat it). Badges
    mark where each Figure 1c safeguard acts. Sources: SKILL.md Rule 8,
    references/step-protocol.md (gates, GATE C, reopen and redo paths), .claude/agents/*.md."""
    W, H = 960, 646
    s = SVG(W, H)

    def node(x, y, w, h, lines, c, size=13):
        s.rect(x, y, w, h, stroke=c, fill=tint(c, 0.12), rx=7, sw=1.5)
        y0 = y + h / 2 - (len(lines) - 1) * size * 0.62 + size * 0.36
        for i, ln in enumerate(lines):
            s.text(x + w / 2, y0 + i * size * 1.24, ln, size=size, fill=INK, anchor="middle",
                   weight="bold" if i == 0 else "normal")

    def diamond(cx, cy, label, c, hw=40, hh=30):
        s.add(f'<polygon points="{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}" '
              f'fill="{tint(c, 0.15)}" stroke="{c}" stroke-width="1.6"/>')
        s.text(cx, cy + 4.5, label, size=13, weight="bold", anchor="middle")

    def label(x, y, t, anchor="start", fill=INK2, bg=False):
        if bg:
            w = len(t) * 6.4 + 8
            x0 = {"start": x - 4, "middle": x - w / 2, "end": x - w + 4}[anchor]
            s.rect(x0, y - 12, w, 17, stroke="none", fill="#fff", rx=3)
        s.text(x, y, t, size=13, fill=fill, anchor=anchor, style="italic")

    def commit(x, y):
        s.add(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="{OCHRE}" '
              f'stroke-width="2.4"/>')

    def vtext(x, y, t, c, size=14):
        s.add(f'<text x="0" y="0" font-size="{size}" font-weight="bold" fill="{c}" '
              f'text-anchor="middle" transform="translate({x},{y}) rotate(-90)">'
              f'{escape(t)}</text>')

    # lanes
    lanes = [("Researcher", ORANGE, 50, 120), ("Main agent", INK2, 170, 140),
             ("Coding agent", AQUA_TXT, 310, 110), ("Critic agent", VIOLET, 420, 110)]
    for name, c, y, h in lanes:
        s.rect(12, y, W - 24, h, stroke="none", fill=tint(c, 0.06), rx=0)
        s.add(f'<line x1="12" y1="{y + h}" x2="{W - 12}" y2="{y + h}" stroke="{LINE}"/>')
        s.add(f'<rect x="12" y="{y}" width="4" height="{h}" fill="{c}"/>')
        vtext(44, y + h / 2, name, c)
    s.add(f'<line x1="72" y1="50" x2="72" y2="530" stroke="{LINE}"/>')

    # phase headers
    s.rect(80, 10, 302, 30, stroke="none", fill=tint(INK2, 0.15), rx=6)
    s.text(231, 30, "PLAN", size=14, weight="bold", anchor="middle")
    s.rect(424, 10, 524, 30, stroke="none", fill=tint(INK2, 0.15), rx=6)
    s.text(686, 30, "RUN — one milestone; methods, analysis, evaluation each repeat it",
           size=14, weight="bold", anchor="middle")

    # ---- Plan
    node(88, 88, 104, 44, ["Research", "question"], ORANGE)
    node(88, 212, 108, 56, ["List KG entries", "by query, not", "from memory"], INK2)
    node(210, 212, 112, 56, ["Write framing:", "hit, miss,", "statistics plan"], INK2)
    node(210, 447, 112, 56, ["Critic reads", "the plan cold"], VIOLET)
    diamond(346, 110, "agree?", ORANGE, hw=34)
    s.arrow([(140, 132), (140, 210)])
    s.arrow([(196, 240), (208, 240)])
    s.arrow([(266, 268), (266, 445)])
    s.arrow([(322, 475), (346, 475), (346, 142)])
    s.arrow([(312, 110), (238, 110), (238, 210)], dash="5 3")
    label(275, 102, "changes", anchor="middle")
    label(340, 336, "delta pass", anchor="end", fill=VIOLET)
    label(340, 352, "after each", anchor="end", fill=VIOLET)
    label(340, 368, "change", anchor="end", fill=VIOLET)
    s.text(170, 370, "not used in planning", size=13, fill=INK2, anchor="middle",
           style="italic")
    icon_badge(s, "database", 199, 207)
    icon_badge(s, "lock", 325, 207)

    # ---- the lock
    s.rect(392, 50, 22, 480, stroke="none", fill=INK, rx=4)
    vtext(407, 300, "PROPOSAL LOCKED", "#fff", size=13)
    s.arrow([(380, 110), (390, 110)], INK, sw=2)
    commit(385, 96)
    icon_badge(s, "lock", 403, 66)

    # ---- Run (one milestone)
    node(428, 88, 100, 44, ["Agree the", "scope"], ORANGE)
    node(428, 337, 130, 56, ["Run scripts and", "KG queries; return", "files + facts only"],
         AQUA_TXT)
    node(588, 212, 116, 56, ["Read the real", "files; judge what", "they show"], INK2)
    node(724, 447, 118, 56, ["Fresh critic", "re-checks claims", "against the files"], VIOLET)
    diamond(890, 110, "approve?", ORANGE, hw=44)

    s.arrow([(478, 132), (478, 335)])
    s.arrow([(558, 365), (620, 365), (620, 270)])
    label(589, 358, "manifest", anchor="middle")
    s.arrow([(588, 232), (534, 232), (534, 335)], dash="5 3")
    label(540, 290, "follow-ups")
    s.arrow([(704, 250), (783, 250), (783, 445)])
    s.arrow([(724, 490), (664, 490), (664, 270)], dash="5 3")
    label(656, 452, "blockers: fix,", anchor="end")
    label(656, 468, "or rebut with data", anchor="end")
    s.arrow([(842, 475), (890, 475), (890, 142)])
    label(896, 320, "clean", fill=VIOLET)
    s.arrow([(890, 80), (890, 68), (478, 68), (478, 86)], dash="5 3")
    label(684, 63, "no: iterate within the milestone, or redo it", anchor="middle")
    s.arrow([(934, 110), (947, 110)], INK, sw=2)
    label(940, 100, "yes", anchor="middle")
    commit(940, 124)
    commit(588, 268)

    # reopen path: a data reveal reopens the locked plan, on the record
    s.arrow([(646, 210), (646, 186), (296, 186), (296, 210)], INK, dash="2 3", sw=1.6)
    label(548, 203, "data contradict the plan → recorded reopening", anchor="middle",
          fill=INK, bg=True)

    icon_badge(s, "check", 425, 332)
    icon_badge(s, "database", 561, 332)
    icon_badge(s, "code", 561, 398)
    icon_badge(s, "magnifier", 708, 207)
    icon_badge(s, "scales", 846, 442)

    # ---- legend
    y = 556
    s.text(24, y + 5, "Safeguards (Fig. 1):", size=13, weight="bold")
    x = 164
    for kind, t in [("database", "KG only"), ("lock", "pre-registered"),
                    ("check", "methods tested"), ("scales", "roles kept apart"),
                    ("magnifier", "verify claims"), ("code", "scripts + history")]:
        icon_badge(s, kind, x + 10, y, r=10)
        s.text(x + 26, y + 5, t, size=13, fill=INK)
        x += 129
    y = 586
    commit(30, y)
    s.text(42, y + 5, "commit: every iteration and approval, never amended", size=13)
    s.arrow([(420, y), (460, y)], INK2, dash="5 3")
    s.text(468, y + 5, "loops back", size=13)
    s.arrow([(572, y), (612, y)], INK, dash="2 3", sw=1.6)
    s.text(620, y + 5, "reopening the locked plan", size=13)
    s.rect(12, 606, W - 24, 28, stroke="none", fill=tint(ORANGE, 0.14), rx=14)
    s.text(W / 2, 625, "The researcher's gates (orange) open and close every step; "
           "no agent closes a step alone.", size=13, weight="bold", anchor="middle")
    s.save("drafts/fig2f_process_swimlanes.svg")


# ---------------------------------------------------------------- Figure 2g
def figure2g():
    """Figure 2f simplified: two lanes (researcher, AI); the coding agent and the critic are
    steps in the AI lane; only the three loops that matter for validity are drawn."""
    W, H = 960, 428
    s = SVG(W, H)

    def node(x, y, w, h, lines, c, size=13):
        s.rect(x, y, w, h, stroke=c, fill=tint(c, 0.12), rx=7, sw=1.5)
        y0 = y + h / 2 - (len(lines) - 1) * size * 0.62 + size * 0.36
        for i, ln in enumerate(lines):
            s.text(x + w / 2, y0 + i * size * 1.24, ln, size=size, fill=INK, anchor="middle",
                   weight="bold" if i == 0 else "normal")

    def diamond(cx, cy, label, c, hw=40, hh=28):
        s.add(f'<polygon points="{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}" '
              f'fill="{tint(c, 0.15)}" stroke="{c}" stroke-width="1.6"/>')
        s.text(cx, cy + 4.5, label, size=13, weight="bold", anchor="middle")

    def label(x, y, t, anchor="start", fill=INK2, bg=False):
        if bg:
            w = len(t) * 6.4 + 8
            x0 = {"start": x - 4, "middle": x - w / 2, "end": x - w + 4}[anchor]
            s.rect(x0, y - 12, w, 17, stroke="none", fill="#fff", rx=3)
        s.text(x, y, t, size=13, fill=fill, anchor=anchor, style="italic")

    def commit(x, y):
        s.add(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="{OCHRE}" '
              f'stroke-width="2.4"/>')

    def vtext(x, y, t, c, size=14):
        s.add(f'<text x="0" y="0" font-size="{size}" font-weight="bold" fill="{c}" '
              f'text-anchor="middle" transform="translate({x},{y}) rotate(-90)">'
              f'{escape(t)}</text>')

    # lanes
    for name, c, y, h in [("Researcher", ORANGE, 50, 110), ("AI", INK2, 160, 150)]:
        s.rect(12, y, W - 24, h, stroke="none", fill=tint(c, 0.06), rx=0)
        s.add(f'<line x1="12" y1="{y + h}" x2="{W - 12}" y2="{y + h}" stroke="{LINE}"/>')
        s.add(f'<rect x="12" y="{y}" width="4" height="{h}" fill="{c}"/>')
        vtext(44, y + h / 2, name, c)
    s.add(f'<line x1="72" y1="50" x2="72" y2="310" stroke="{LINE}"/>')

    # phase headers
    s.rect(80, 10, 302, 30, stroke="none", fill=tint(INK2, 0.15), rx=6)
    s.text(231, 30, "PLAN", size=14, weight="bold", anchor="middle")
    s.rect(424, 10, 524, 30, stroke="none", fill=tint(INK2, 0.15), rx=6)
    s.text(686, 30, "RUN — repeated for methods, analysis, evaluation",
           size=14, weight="bold", anchor="middle")

    # ---- Plan
    node(88, 83, 100, 44, ["Research", "question"], ORANGE)
    node(88, 207, 124, 56, ["Ground in the KG;", "write the framing"], INK2)
    node(234, 207, 100, 56, ["Fresh critic", "reviews plan"], VIOLET)
    diamond(284, 105, "agree?", ORANGE, hw=36)
    s.arrow([(138, 127), (138, 205)])
    s.arrow([(212, 235), (232, 235)])
    s.arrow([(284, 207), (284, 135)])
    s.arrow([(248, 105), (200, 105), (200, 205)], dash="5 3")
    label(224, 97, "changes", anchor="middle")
    icon_badge(s, "database", 108, 207)
    icon_badge(s, "lock", 212, 207)

    # ---- the lock
    s.rect(392, 50, 22, 260, stroke="none", fill=INK, rx=4)
    vtext(407, 180, "PROPOSAL LOCKED", "#fff", size=13)
    s.arrow([(320, 105), (390, 105)], INK, sw=2)
    label(356, 97, "yes", anchor="middle")
    commit(356, 118)

    # ---- Run
    node(432, 83, 96, 44, ["Agree the", "scope"], ORANGE)
    node(432, 207, 124, 56, ["Coding agent runs", "scripts; returns files"], AQUA_TXT)
    node(578, 207, 120, 56, ["Main AI reads the", "files and judges"], INK2)
    node(720, 207, 104, 56, ["Fresh critic", "checks claims"], VIOLET)
    diamond(884, 105, "approve?", ORANGE, hw=44)
    s.arrow([(480, 127), (480, 205)])
    s.arrow([(556, 235), (576, 235)])
    s.arrow([(698, 235), (718, 235)])
    s.arrow([(824, 235), (884, 235), (884, 135)])
    s.arrow([(884, 77), (884, 64), (480, 64), (480, 81)], dash="5 3")
    label(682, 58, "no: iterate, or redo the milestone", anchor="middle")
    s.arrow([(928, 105), (947, 105)], INK, sw=2)
    label(936, 136, "yes", anchor="middle")
    commit(938, 120)
    icon_badge(s, "check", 452, 207)
    icon_badge(s, "code", 556, 207)
    icon_badge(s, "magnifier", 698, 207)
    icon_badge(s, "scales", 824, 207)

    # reopen path
    s.arrow([(638, 263), (638, 288), (160, 288), (160, 265)], INK, dash="2 3", sw=1.6)
    label(560, 302, "data contradict the plan → recorded reopening", anchor="middle",
          fill=INK)

    # ---- legend
    y = 338
    s.text(24, y + 5, "Safeguards (Fig. 1):", size=13, weight="bold")
    x = 164
    for kind, t in [("database", "KG only"), ("lock", "pre-registered"),
                    ("check", "methods tested"), ("scales", "roles kept apart"),
                    ("magnifier", "verify claims"), ("code", "scripts + history")]:
        icon_badge(s, kind, x + 10, y, r=10)
        s.text(x + 26, y + 5, t, size=13, fill=INK)
        x += 129
    y = 366
    commit(30, y)
    s.text(42, y + 5, "commit: every iteration and approval, never amended", size=13)
    s.arrow([(420, y), (460, y)], INK2, dash="5 3")
    s.text(468, y + 5, "loops back", size=13)
    s.arrow([(572, y), (612, y)], INK, dash="2 3", sw=1.6)
    s.text(620, y + 5, "reopening the locked plan", size=13)
    s.rect(12, 388, W - 24, 28, stroke="none", fill=tint(ORANGE, 0.14), rx=14)
    s.text(W / 2, 407, "The researcher's gates (orange) open and close every step; "
           "the AI never closes a step alone.", size=13, weight="bold", anchor="middle")
    s.save("drafts/fig2g_process_simple.svg")


# ---------------------------------------------------------------- Figure 2h
# Reader-facing Figure 2g (panel A) plus panel B: what the frozen plan fixes in advance,
# shown on a worked example. Panel B source:
# analyses/2026-11-03-ntca_urea_response/proposal.md (Framing) and its plan commits
# (decision rule committed 792866c -> approved 71fc4ab -> control added 1958831 -> a reviewer
# saw MED4 ntcA during the delta pass; only the controls changed, disclosed -> re-approved 4236f21).
FRAMING_EXAMPLE = [
    ("Hypothesis", "the gene switches on with urea"),
    ("Positive control", "urea-use genes must switch on"),
    ("Negative control", "growth genes must stay flat"),
    ("Statistics plan", "no new test; the original study's verdicts"),
    ("Decision rule", "four outcomes, named in advance"),
    ("Fair comparison", "each strain vs its own control"),
]


def figure2h():
    W, H = 960, 622
    s = SVG(W, H)

    def node(x, y, w, h, lines, c, size=13):
        # uniform weight: node text is one sentence wrapped over lines, so no line is a title
        s.rect(x, y, w, h, stroke=c, fill=tint(c, 0.12), rx=7, sw=1.5)
        y0 = y + h / 2 - (len(lines) - 1) * size * 0.62 + size * 0.36
        for i, ln in enumerate(lines):
            s.text(x + w / 2, y0 + i * size * 1.24, ln, size=size, fill=INK, anchor="middle")

    def diamond(cx, cy, label, c, hw=40, hh=28):
        s.add(f'<polygon points="{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}" '
              f'fill="{tint(c, 0.15)}" stroke="{c}" stroke-width="1.6"/>')
        s.text(cx, cy + 4.5, label, size=13, weight="bold", anchor="middle")

    def label(x, y, t, anchor="start", fill=INK2):
        s.text(x, y, t, size=13, fill=fill, anchor=anchor, style="italic")

    def commit(x, y):
        s.add(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="{OCHRE}" '
              f'stroke-width="2.4"/>')

    def vtext(x, y, t, c, size=14):
        s.add(f'<text x="0" y="0" font-size="{size}" font-weight="bold" fill="{c}" '
              f'text-anchor="middle" transform="translate({x},{y}) rotate(-90)">'
              f'{escape(t)}</text>')

    def panel_letter(x, y, t):
        s.text(x, y, t, size=18, weight="bold")

    # ================= panel A: the process
    panel_letter(14, 31, "A")
    s.rect(80, 10, 326, 30, stroke="none", fill=tint(INK2, 0.15), rx=6)
    s.text(243, 30, "1 · Plan the study", size=14, weight="bold", anchor="middle")
    s.rect(446, 10, 502, 30, stroke="none", fill=tint(INK2, 0.15), rx=6)
    s.text(697, 30, "2 · Run it, stage by stage: build the method, analyse, evaluate",
           size=14, weight="bold", anchor="middle")

    for name, c, y, h in [("Researcher", ORANGE, 50, 110), ("AI assistant", INK2, 160, 150)]:
        s.rect(12, y, W - 24, h, stroke="none", fill=tint(c, 0.06), rx=0)
        s.add(f'<line x1="12" y1="{y + h}" x2="{W - 12}" y2="{y + h}" stroke="{LINE}"/>')
        s.add(f'<rect x="12" y="{y}" width="4" height="{h}" fill="{c}"/>')
        vtext(44, y + h / 2, name, c)
    s.add(f'<line x1="72" y1="50" x2="72" y2="310" stroke="{LINE}"/>')

    # plan: three boxes, 18-unit gaps (same as the run lane)
    node(84, 83, 96, 44, ["Research", "question"], ORANGE)
    node(84, 200, 96, 70, ["Explore what", "the data can", "show"], INK2)
    node(198, 200, 92, 70, ["Set success", "criteria", "(see B)"], INK2)
    node(308, 200, 96, 70, ["AI reviewer,", "new to the", "work, checks", "the plan"], VIOLET)
    diamond(334, 105, "approve?", ORANGE, hw=40)
    s.arrow([(132, 127), (132, 198)])
    s.arrow([(180, 235), (196, 235)])
    s.arrow([(290, 235), (306, 235)])
    s.arrow([(334, 200), (334, 135)])
    s.arrow([(294, 105), (244, 105), (244, 198)], dash="5 3")
    label(269, 97, "revise", anchor="middle")
    icon_badge(s, "database", 100, 200)
    icon_badge(s, "bars", 180, 200, c=MAGENTA)
    icon_badge(s, "lock", 290, 200)

    # freeze
    s.rect(416, 50, 22, 260, stroke="none", fill=INK, rx=4)
    vtext(431, 180, "PLAN FROZEN", "#fff", size=13)
    s.arrow([(374, 105), (414, 105)], INK, sw=2)
    label(394, 97, "yes", anchor="middle")
    commit(394, 118)

    # run
    node(452, 80, 100, 50, ["Agree what this", "stage will do"], ORANGE)
    node(452, 200, 124, 70, ["Coding AI runs", "the analysis code;", "returns output files"],
         AQUA_TXT)
    node(594, 200, 118, 70, ["Main AI reads", "the output files", "and judges them"], INK2)
    node(730, 200, 108, 70, ["AI reviewer,", "new to the work,", "re-checks claims"], VIOLET)
    diamond(890, 105, "approve?", ORANGE, hw=42)
    s.arrow([(502, 130), (502, 198)])
    s.arrow([(576, 235), (592, 235)])
    s.arrow([(712, 235), (728, 235)])
    s.arrow([(838, 235), (890, 235), (890, 135)])
    s.arrow([(890, 77), (890, 64), (502, 64), (502, 78)], dash="5 3")
    label(696, 58, "no: revise, or redo this stage", anchor="middle")
    s.arrow([(932, 105), (947, 105)], INK, sw=2)
    label(940, 92, "yes", anchor="middle")
    commit(940, 120)
    icon_badge(s, "check", 470, 200)
    icon_badge(s, "code", 576, 200)
    icon_badge(s, "magnifier", 712, 200)
    icon_badge(s, "scales", 838, 200)

    s.arrow([(653, 270), (653, 290), (244, 290), (244, 272)], INK, dash="2 3", sw=1.6)
    label(696, 304, "results contradict the plan → plan reopened; the change is recorded",
          anchor="middle", fill=INK)

    # ================= legend (applies to panel A): an aligned grid, columns sized to text
    y = 330
    s.text(24, y + 5, "Safeguards (Fig. 1):", size=13, weight="bold")
    items = [("database", "KG data only", None), ("bars", "scope first", MAGENTA),
             ("lock", "criteria set first", None), ("check", "method tested", None),
             ("scales", "doing ≠ judging", None), ("magnifier", "claims checked", None),
             ("code", "full history", None)]
    ncol = 4
    colw = [max(len(items[i][1]) for i in range(c, len(items), ncol)) * 7 + 58
            for c in range(ncol)]
    for i, (kind, t, c) in enumerate(items):
        x = 160 + sum(colw[:i % ncol])
        yy = y + (i // ncol) * 26
        icon_badge(s, kind, x + 10, yy, r=10, c=c)
        s.text(x + 26, yy + 5, t, size=13, fill=INK)
    y = 384
    commit(30, y)
    s.text(42, y + 5, "saved to version history; never overwritten", size=13)
    s.arrow([(360, y), (400, y)], INK2, dash="5 3")
    s.text(408, y + 5, "revision loop", size=13)
    s.arrow([(530, y), (570, y)], INK, dash="2 3", sw=1.6)
    s.text(578, y + 5, "reopening the frozen plan", size=13)

    # ================= panel B: the frozen plan, drawn as a document (not a diagram)
    top, x0, x1, fold = 414, 12, W - 12, 18
    bot = top + 150
    s.add(f'<path d="M{x0},{top} H{x1 - fold} L{x1},{top + fold} V{bot} H{x0} Z" '
          f'fill="{tint(SLATE, 0.05)}" stroke="{SLATE}" stroke-width="1.5"/>')
    s.add(f'<path d="M{x1 - fold},{top} V{top + fold} H{x1}" fill="{tint(SLATE, 0.25)}" '
          f'stroke="{SLATE}" stroke-width="1.5"/>')
    s.add(f'<path d="M{x0},{top} H{x1 - fold - 1} V{top + 30} H{x0} Z" fill="{SLATE}"/>')
    s.text(x0 + 12, top + 21, "B", size=17, weight="bold", fill="#fff")
    s.text(x0 + 34, top + 21, "The frozen plan: fixed before the result is scored", size=15,
           weight="bold", fill="#fff")
    s.text(x1 - fold - 10, top + 21, "example: does a nitrogen-control gene switch on when "
           "bacteria are fed urea?", size=13, style="italic", fill="#fff", anchor="end")
    for i, (head, ex) in enumerate(FRAMING_EXAMPLE):
        x = x0 + 24 + (i // 3) * 462
        y = top + 56 + (i % 3) * 26
        s.rect(x, y - 11, 12, 12, stroke=SLATE, fill="#fff", rx=2, sw=1.4)
        s.add(f'<path d="M{x + 2.5},{y - 5} L{x + 5},{y - 2} L{x + 10},{y - 9}" fill="none" '
              f'stroke="{SLATE}" stroke-width="1.8" stroke-linecap="round"/>')
        s.add(f'<text x="{x + 20}" y="{y}" font-size="14" fill="{INK}">'
              f'<tspan font-weight="bold" fill="{SLATE}">{escape(head)}:</tspan> '
              f'{escape(ex)}</text>')
    s.add(f'<line x1="{x0 + 24}" y1="{top + 124}" x2="{x1 - 24}" y2="{top + 124}" '
          f'stroke="{tint(SLATE, 0.3)}"/>')
    commit(x0 + 30, top + 138)
    s.text(x0 + 44, top + 143, "History: decision rule committed and approved → control added → "
           "a reviewer saw one value → only the controls changed, disclosed → re-approved.",
           size=13, fill=INK2, style="italic")

    # ================= banner
    s.rect(12, 584, W - 24, 28, stroke="none", fill=tint(ORANGE, 0.14), rx=14)
    s.text(W / 2, 603, "The researcher approves every plan and every stage; the AI never "
           "moves on alone.", size=14, weight="bold", anchor="middle")
    s.save("drafts/fig2h_process_framing.svg")


# ---------------------------------------------------------------- Figure 2 (safeguards)
# The process (Plan -> Run) with each AI step wearing the Figure 1 card it carries, plus
# panel B: what "Pre-register the test" fixes. Spec:
# docs/superpowers/specs/2026-11-22-paper-process-figure-design.md
def card(title):
    """The Figure 1 card with this title (colour, icon, title stay in one place)."""
    return {c["title"]: c for c in CARDS}[title]


def figure2_safeguards():
    W = 960
    BW, BH, GAP = 112, 136, 10          # AI box width / height, gap between boxes
    AY = 172                            # AI box top
    PLAN_X = [64 + i * (BW + GAP) for i in range(4)]
    BAR_X = PLAN_X[-1] + BW + 10
    RUN_X = [BAR_X + 32 + i * (BW + GAP) for i in range(3)]
    assert RUN_X[-1] + BW <= W - 12

    # panel B layout first, so the canvas height is known
    by = 384
    bx, shw, RH = 40, 600, 25         # sheet x, width, row height
    bh = 34 + len(FRAMING) * RH + 10
    s = SVG(W, round(by + bh + 12))

    def vtext(x, y, t, c, size=14):
        s.add(f'<text x="0" y="0" font-size="{size}" font-weight="bold" fill="{c}" '
              f'text-anchor="middle" transform="translate({x},{y}) rotate(-90)">'
              f'{escape(t)}</text>')

    def label(x, y, t, anchor="start", fill=INK2):
        s.text(x, y, t, size=13, fill=fill, anchor=anchor, style="italic")

    def ring(x, y):                     # "on the record" (Fig 1's frame colour)
        s.add(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="{ORANGE}" '
              f'stroke-width="2.4"/>')

    def card_box(x, y, w, h, c):        # Fig 1 card treatment: thick left edge, tint, outline
        s.rect(x, y, w, h, stroke="none", fill=c, rx=8)
        s.rect(x + 4, y, w - 4, h, stroke="none", fill=tint(c, 0.06), rx=8)
        s.rect(x, y, w, h, stroke=c, fill="none", sw=1.5, rx=8)

    def ai_box(x, title, step):
        cd = card(title)
        c = cd["color"]
        card_box(x, AY, BW, BH, c)
        k = 1.1
        s.add(f'<g transform="translate({x + BW / 2 + 2 - 12 * k},{AY + 9}) scale({k})">')
        icon_cards(s, cd["icon"], 0, 0, c)
        s.add("</g>")
        cx, inner = x + BW / 2 + 2, BW - 16
        tl = wrap(cd["title"], inner, 14, k=0.56)
        assert len(tl) <= 2, tl
        ty = AY + 54 + (2 - len(tl)) * 8.5
        for i, ln in enumerate(tl):
            s.text(cx, ty + i * 17, ln, size=14, weight="bold", fill=c, anchor="middle")
        s.add(f'<path d="M{x + 12},{AY + 82} H{x + BW - 8}" stroke="{tint(c, 0.4)}"/>')
        sl = wrap(step, inner, 13, k=0.48)
        assert len(sl) <= 3, sl
        for i, ln in enumerate(sl):
            s.text(cx, AY + 100 + i * 16, ln, size=13, anchor="middle")

    def r_box(x, y, w, h, lines):       # researcher step (Fig 1's orange pill colours)
        assert all(len(ln) * 13 * 0.45 <= w - 10 for ln in lines), lines  # 0.45: measured
        s.rect(x, y, w, h, stroke=ORANGE, fill=tint(ORANGE, 0.14), rx=8)
        y0 = y + h / 2 - (len(lines) - 1) * 13 * 0.62 + 13 * 0.36
        for i, ln in enumerate(lines):
            s.text(x + w / 2, y0 + i * 13 * 1.24, ln, size=13, anchor="middle")

    def diamond(cx, cy, hw=40, hh=26):
        s.add(f'<polygon points="{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}" '
              f'fill="{tint(ORANGE, 0.14)}" stroke="{ORANGE}" stroke-width="1.6"/>')
        s.text(cx, cy + 4.5, "approve?", size=13, weight="bold", anchor="middle")

    # ================= panel A
    s.text(14, 31, "A", size=18, weight="bold")
    px0, px1 = PLAN_X[0], PLAN_X[-1] + BW
    rx0, rx1 = RUN_X[0], W - 12
    s.rect(px0, 10, px1 - px0, 30, stroke="none", fill=tint(INK2, 0.15), rx=6)
    s.text((px0 + px1) / 2, 30, "1 · Plan the study", size=14, weight="bold", anchor="middle")
    s.rect(rx0, 10, rx1 - rx0, 30, stroke="none", fill=tint(INK2, 0.15), rx=6)
    s.text((rx0 + rx1) / 2, 30, "2 · Run it ×3: build the method, analyse, evaluate", size=14,
           weight="bold", anchor="middle")
    LANE_END = 348
    for name, c, y, h in [("Researcher", ORANGE, 50, 100), ("AI", INK2, 150, LANE_END - 150)]:
        s.rect(12, y, W - 24, h, stroke="none", fill=tint(c, 0.06), rx=0)
        s.add(f'<line x1="12" y1="{y + h}" x2="{W - 12}" y2="{y + h}" stroke="{LINE}"/>')
        s.add(f'<rect x="12" y="{y}" width="4" height="{h}" fill="{c}"/>')
        vtext(38, y + h / 2, name, c)
    s.rect(BAR_X, 50, 22, LANE_END - 50, stroke="none", fill=INK, rx=4)
    vtext(BAR_X + 15, (50 + LANE_END) / 2, "PLAN FROZEN", "#fff", size=13)

    def mid(x):
        return x + BW / 2
    ym = AY + BH / 2
    # plan
    for x, (t, step) in zip(PLAN_X, [
            ("Look it up", "Show what the KG holds"),
            ("Scope first", "Check the approach can work"),
            ("Pre-register the test", "Fix controls and decision rule (B)"),
            ("Separate the roles", "Fresh AI reviews the plan")]):
        ai_box(x, t, step)
    for a, b in zip(PLAN_X, PLAN_X[1:]):
        s.arrow([(a + BW, ym), (b - 1, ym)])
    r_box(PLAN_X[0], 76, BW, 46, ["Research", "question"])
    for x in PLAN_X[:3]:                # each plan step is a dialog the researcher confirms
        s.arrow([(x + 26, 142), (x + 26, AY - 2)], ORANGE, sw=1.6, both=True)
    s.text(PLAN_X[1] + 6, 120, "a dialog: the researcher", size=13, fill=ORANGE_TXT, style="italic")
    s.text(PLAN_X[1] + 6, 136, "confirms each step", size=13, fill=ORANGE_TXT,
           style="italic")
    s.arrow([(mid(PLAN_X[0]), 122), (mid(PLAN_X[0]), AY - 2)])
    pa = mid(PLAN_X[3])
    diamond(pa, 100)
    s.arrow([(pa, AY), (pa, 128)])
    s.arrow([(pa - 40, 100), (mid(PLAN_X[2]), 100), (mid(PLAN_X[2]), AY - 2)], dash="5 3")
    label((pa - 40 + mid(PLAN_X[2])) / 2, 92, "revise", anchor="middle")
    s.arrow([(pa + 40, 100), (BAR_X - 2, 100)], INK, sw=2)
    ring((pa + 40 + BAR_X) / 2, 113)

    # run
    for x, (t, step) in zip(RUN_X, [
            ("Check the computation", "Coding AI runs it, returns files"),
            ("Claims match evidence", "Main AI reads files, judges"),
            ("Separate the roles", "Fresh AI re-checks claims")]):
        ai_box(x, t, step)
    s.arrow([(RUN_X[0] + BW, ym), (RUN_X[1] - 1, ym)])
    r_box(RUN_X[0], 76, BW, 46, ["Agree what this", "stage does"])
    s.arrow([(mid(RUN_X[0]), 122), (mid(RUN_X[0]), AY - 2)])
    r_box(RUN_X[1], 76, BW, 46, ["Explore the", "results together"])
    s.arrow([(mid(RUN_X[1]), AY), (mid(RUN_X[1]), 124)])
    xe = RUN_X[2] + 22
    s.arrow([(RUN_X[1] + BW, 99), (xe, 99), (xe, AY - 2)])
    ra = mid(RUN_X[2]) + 14
    diamond(ra, 100, hw=36)
    s.arrow([(ra, AY), (ra, 128)])
    s.arrow([(ra, 74), (ra, 70), (mid(RUN_X[0]), 70), (mid(RUN_X[0]), 74)], dash="5 3")
    label((ra + mid(RUN_X[0])) / 2, 64, "no: revise or redo this stage", anchor="middle")
    s.arrow([(ra + 36, 100), (W - 13, 100)], INK, sw=2)
    ring(ra + 36 + 6, 113)

    # reopen: results contradict the frozen plan
    yr = AY + BH + 14
    s.arrow([(mid(RUN_X[1]), AY + BH), (mid(RUN_X[1]), yr), (mid(PLAN_X[2]), yr),
             (mid(PLAN_X[2]), AY + BH + 2)], INK, dash="2 3", sw=1.6)
    s.add(f'<path d="M{BAR_X},{yr} H{BAR_X + 22}" stroke="#fff" stroke-width="1.6" '
          f'stroke-dasharray="2 3"/>')
    label(W - 20, yr + 17, "results contradict the plan → plan reopened, change recorded",
          anchor="end", fill=INK)
    ring(PLAN_X[0] + 6, 364)
    s.text(PLAN_X[0] + 18, 368.5, "every approval is saved: everything is on the record",
           size=13, fill=INK2)

    # ================= panel B: the plan as a locked sheet (what "Pre-register the test" fixes)
    pr = card("Pre-register the test")
    c = pr["color"]
    s.text(14, by + 24, "B", size=18, weight="bold")
    s.rect(bx, by, shw, bh, stroke=c, fill="#fff", rx=8, sw=1.5)
    s.rect(bx, by, shw, 34, stroke="none", fill=c, rx=8)
    s.rect(bx, by + 20, shw, 14, stroke="none", fill=c, rx=0)
    s.add(f'<g transform="translate({bx + 12},{by + 6}) scale(0.92)">')
    icon_cards(s, pr["icon"], 0, 0, "#fff")
    s.add("</g>")
    s.text(bx + 44, by + 23, pr["title"], size=16, weight="bold", fill="#fff")
    sub = "— the plan, before the result is seen"
    sx = bx + 44 + len(pr["title"]) * 16 * 0.47 + 8
    assert sx + len(sub) * 14 * 0.5 <= bx + shw - 12
    s.text(sx, by + 23, sub, size=14, fill="#fff")
    stamp_l = bx + shw - 150
    for i, (head, frag) in enumerate(FRAMING):
        yy = by + 34 + i * RH
        s.text(bx + 16, yy + 18, head, size=14, weight="bold")
        assert bx + 196 + (len(frag) + 2) * 14 * 0.48 <= stamp_l, frag
        s.text(bx + 196, yy + 18, f"“{frag}”", size=14, style="italic")
        if i < len(FRAMING) - 1:
            s.add(f'<path d="M{bx + 16},{yy + RH} H{bx + shw - 16}" stroke="{tint(c, 0.25)}"/>')
    scx, scy = bx + shw - 82, by + 34 + 3.5 * RH
    s.add(f'<g transform="rotate(-10 {scx} {scy})">'
          f'<rect x="{scx - 62}" y="{scy - 20}" width="124" height="40" rx="6" fill="#fff" '
          f'fill-opacity="0.85" stroke="{c}" stroke-width="3"/>'
          f'<text x="{scx}" y="{scy + 7}" font-size="20" font-weight="bold" fill="{c}" '
          f'text-anchor="middle" letter-spacing="3">FROZEN</text></g>')
    # run order: the skill's sentence, split into its three steps
    x0, x1 = bx + shw + 36, W - 12
    s.text((x0 + x1) / 2, by + 18, "Run order", size=14, weight="bold", anchor="middle")
    steps = [t.strip().rstrip(".") for t in FRAMING_FOOTER.split("→")]
    shades = [c, "#6b7888", "#8c97a4"]
    ch, cy = 52, by + 30
    for t, f in zip(steps, shades):
        xm = (x0 + x1) / 2
        s.add(f'<polygon points="{x0},{cy} {x1},{cy} {x1},{cy + ch - 12} {xm},{cy + ch} '
              f'{x0},{cy + ch - 12}" fill="{f}"/>')
        assert len(t) * 14 * 0.55 <= x1 - x0 - 16, t
        s.text(xm, cy + (ch - 12) / 2 + 5, t, size=14, weight="bold", fill="#fff",
               anchor="middle")
        cy += ch + 4
    assert cy <= by + bh + 4, (cy, by + bh)
    s.save("fig2_process_safeguards.svg")


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
    s.save("drafts/fig2_process.svg")


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
    s.save("drafts/fig2b_concepts_workflow.svg")


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
    s.save("drafts/fig2c_flow_concepts.svg")


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
    s.save("drafts/fig2d_concepts_in_flow.svg")


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
    s.save("drafts/fig2e_concepts_two_rows.svg")


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
    s.save("drafts/fig3_agents.svg")

# ---------------------------------------------------------------- Supplementary Figure S1
# How Spock's AIs are wired, for technical reviewers (sources: .claude/agents/*.md,
# references/research-notebook.md "Code review", references/step-protocol.md). Same visual
# language as Figures 1-2: researcher orange, KG blue, record ring orange; helper AIs neutral.
def figureS1():
    W, H = 960, 500
    s = SVG(W, H)

    def box(x, y, w, h, title, sub, bullets, c, tc=None, size=14):
        s.rect(x, y, w, h, stroke=c, fill=tint(c, 0.07), sw=1.8, rx=8)
        s.text(x + 12, y + 22, title, size=16, weight="bold", fill=tc or c)
        yy = y + 22
        if sub:
            tw = len(title) * 16 * 0.55
            s.text(x + 12 + tw + 8, y + 22, sub, size=13, fill=INK2)
        yy += size + 6
        for b in bullets:
            for k, ln in enumerate(wrap(b, w - 34, size, k=0.46)):
                s.text(x + 14, yy, "•" if k == 0 else "", size=size)
                s.text(x + 26, yy, ln, size=size)
                yy += size * 1.3
            yy += 2
        assert yy - size * 1.3 <= y + h - 6, (title, yy, y + h)

    # researcher and main AI
    box(12, 160, 118, 160, "Researcher", None, ["owns the question", "agrees each step",
                                                "approves"], ORANGE, size=13)
    box(176, 20, 210, 420, "Main AI", None,
        ["Claude + the research-methodology skill", "owns all judgment",
         "reads the real data files", "writes notebook and paper",
         "records a response to every finding", "commits each approved step",
         "the only voice to the researcher"], INK, INK)
    s.arrow([(132, 240), (174, 240)], ORANGE, both=True, sw=2)
    s.text(153, 230, "dialog", size=13, fill=ORANGE_TXT, anchor="middle")

    # helper AIs: plan reviewer, then the run-stage helpers in the order they act
    AX, AW, AH, AG = 520, 262, 98, 8
    agents = [
        ("proposal-critic", "plan reviewer",
         ["fresh context; read-only",
          "limited KG tools: cannot open the results"],
         "plan", "findings", "reads"),
        ("kg-coder", "coding AI",
         ["kept across a stage; same rules", "writes scripts, data, figures",
          "never interprets or commits"],
         "task", "facts only", "writes"),
        ("code reviewer", "fresh AI",
         ["not the code's author", "reads method and statistics code against the plan "
          "and the data"],
         "code", "findings", "reads"),
        ("critic", "stage reviewer",
         ["fresh context every pass", "cannot edit; checks claims against the files"],
         "scope + lens", "findings", "reads"),
    ]
    for i, (name, sub, bullets, out, back, io) in enumerate(agents):
        y = 20 + i * (AH + AG)
        box(AX, y, AW, AH, name, sub, bullets, INK2, INK, size=13)
        s.arrow([(388, y + 34), (AX - 2, y + 34)], INK2, sw=1.8)
        s.text(453, y + 27, out, size=13, fill=INK2, anchor="middle")
        s.arrow([(AX - 2, y + 66), (388, y + 66)], INK2, sw=1.8)
        s.text(453, y + 84, back, size=13, fill=INK2, anchor="middle", style="italic")
        s.arrow([(AX + AW + 2, y + AH / 2), (820, y + AH / 2)], INK2, sw=1.6,
                both=(io == "writes"))
        s.text(801, y + AH / 2 - 8, io, size=13, fill=INK2, anchor="middle")

    # shared: files + git (on the record) and the KG (Look it up)
    s.rect(824, 20, 124, 420, stroke=LINE, fill="#f5f5f3", rx=8)
    s.text(886, 46, "Shared", size=15, weight="bold", fill=INK2, anchor="middle")
    s.rect(834, 64, 104, 160, stroke=ORANGE, fill=BG, rx=8)
    s.text(886, 98, "Files", size=16, weight="bold", anchor="middle")
    s.text(886, 118, "+ git", size=14, anchor="middle")
    s.add(f'<circle cx="886" cy="146" r="7" fill="#fff" stroke="{ORANGE}" stroke-width="2.6"/>')
    for j, ln in enumerate(["every approval", "saved: on the", "record"]):
        s.text(886, 176 + j * 16, ln, size=13, fill=INK2, anchor="middle")
    kg = card("Look it up")
    s.rect(834, 240, 104, 186, stroke=BLUE, fill=tint(BLUE, 0.08), rx=8)
    s.add('<g transform="translate(870,252) scale(1.3)">')
    icon_cards(s, kg["icon"], 0, 0, BLUE)
    s.add("</g>")
    for j, ln in enumerate(["Knowledge", "graph"]):
        s.text(886, 310 + j * 19, ln, size=16, weight="bold", fill=BLUE, anchor="middle")
    for j, ln in enumerate(["the only data", "source; MCP +", "Python API"]):
        s.text(886, 360 + j * 16, ln, size=13, fill=INK2, anchor="middle")

    # the Separate-the-roles message, in Figure 1's colour and icon
    sr = card("Separate the roles")
    s.rect(12, 452, W - 24, 36, stroke="none", fill=tint(sr["color"], 0.1), rx=18)
    s.add('<g transform="translate(28,457) scale(1.05)">')
    icon_cards(s, sr["icon"], 0, 0, sr["color"])
    s.add("</g>")
    msg = ("Separate the roles: the coder cannot conclude, the reviewers cannot edit, "
           "only the main AI speaks to the researcher.")
    assert 62 + len(msg) * 14 * 0.5 <= W - 24, len(msg)
    s.text(62, 475, msg, size=14, weight="bold", fill=sr["color"])
    s.save("figS1_agents.svg")


if __name__ == "__main__":
    figure1_cards("a")
    figure2_safeguards()
    figureS1()
    figure1()
    figure1b()
    figure1c()
    figure1e()
    figure2f()
    figure2g()
    figure2h()
    figure2()
    figure2b()
    figure2c()
    figure2d()
    figure2e()
    figure3()
