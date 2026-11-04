"""Final 3-slide presentation: question & approach / results / conclusion.

Usage: python build_final_three.py <out.pptx>
All numbers from the pilot and expression data files (see methods/notebook.md).
"""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION

out = sys.argv[1]; FIG = Path(__file__).resolve().parent
INK = RGBColor(0x1F, 0x23, 0x28); MUTED = RGBColor(0x59, 0x63, 0x6E)
PRO = RGBColor(0x1F, 0x8A, 0x4C); PRO_L = RGBColor(0xE5, 0xF4, 0xEA)
HET = RGBColor(0x1D, 0x5F, 0xAE); HET_L = RGBColor(0xE6, 0xEE, 0xF9)
UP = RGBColor(0xD9, 0x71, 0x1C); UP_L = RGBColor(0xFD, 0xF1, 0xE6)
DARK = RGBColor(0x12, 0x2B, 0x1E); WHITE = RGBColor(0xFF, 0xFF, 0xFF); PANEL = RGBColor(0xF3, 0xF4, 0xF6)
WARN = RGBColor(0x9A, 0x67, 0x00); WARN_L = RGBColor(0xFD, 0xF3, 0xDC)
HEAD, BODY = "Cambria", "Calibri"

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
W, H = prs.slide_width, prs.slide_height; blank = prs.slide_layouts[6]

def tb(s, x, y, w, h, paras, size=16, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name=None, after=6):
    t = s.shapes.add_textbox(x, y, w, h)
    if name: t.name = name
    tf = t.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, p in enumerate(paras if isinstance(paras, list) else [paras]):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align; para.space_after = Pt(after)
        for seg in (p if isinstance(p, list) else [(p, {})]):
            txt, o = seg if isinstance(seg, tuple) else (seg, {})
            r = para.add_run(); r.text = txt
            r.font.size = Pt(o.get("size", size)); r.font.name = o.get("font", font)
            r.font.bold = o.get("bold", bold); r.font.italic = o.get("italic", False)
            r.font.color.rgb = o.get("color", color)
    return t

def box(s, x, y, w, h, fill, line=None, name=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    b = s.shapes.add_shape(shape, x, y, w, h)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: b.adjustments[0] = 0.07
    b.fill.solid(); b.fill.fore_color.rgb = fill
    if line is None: b.line.fill.background()
    else: b.line.color.rgb = line; b.line.width = Pt(2)
    b.shadow.inherit = False
    if name: b.name = name
    return b

def num(s, x, y, n, colr, name):
    c = box(s, x, y, Inches(0.55), Inches(0.55), colr, shape=MSO_SHAPE.OVAL, name=name)
    c.text_frame.text = str(n); p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.runs[0]; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = BODY
    c.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

# ================= Slide 1: question & approach =================
s = prs.slides.add_slide(blank)
bg = box(s, 0, 0, W, H, DARK, shape=MSO_SHAPE.RECTANGLE, name="Background")
tb(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.5), "AMINO-ACID UTILIZATION IN PROCHLOROCOCCUS  ·  D. AHARONOVICH  ·  NOV 2026", size=14, bold=True, color=RGBColor(0x9F, 0xD4, 0xB2), name="Kicker")
tb(s, Inches(0.7), Inches(1.0), Inches(12), Inches(1.7),
   [[("Can ", {}), ("Prochlorococcus", {"italic": True}), (" use amino acids as a nitrogen source, and do strains differ?", {})]],
   size=36, font=HEAD, bold=True, color=WHITE, name="Question")
tb(s, Inches(0.7), Inches(2.75), Inches(12), Inches(0.5),
   "Motivation: my growth experiments on amino acids as the only N source. Here: what do genomes and existing experiments in the lab database say?",
   size=17, color=RGBColor(0xB9, 0xE3, 0xC8), name="Motivation")
appr = [("Breakdown genes", "58 breakdown pathways for 20 amino acids; only enzymes used solely for breakdown count", "MED4 · MIT9313 · Alteromonas", PRO),
        ("Uptake genes", "Amino-acid transporters, by amino-acid group, and whether they sit next to breakdown genes", "MED4 vs E. coli", PRO),
        ("Experiments", "Do amino-acid genes switch on when nitrogen is short?", "10 MED4 nitrogen and coculture experiments", UP)]
x0, y0, cw, ch, gap = Inches(0.7), Inches(3.75), Inches(3.85), Inches(2.85), Inches(0.19)
for i, (h, d, which, colr) in enumerate(appr):
    x = x0 + i * (cw + gap)
    box(s, x, y0, cw, ch, WHITE, name=f"Approach {i+1} card")
    num(s, x + Inches(0.3), y0 + Inches(0.3), i + 1, colr, f"Approach {i+1} number")
    tb(s, x + Inches(1.05), y0 + Inches(0.33), cw - Inches(1.3), Inches(0.5), h, size=22, bold=True, font=HEAD, color=colr, name=f"Approach {i+1} title")
    tb(s, x + Inches(0.3), y0 + Inches(1.1), cw - Inches(0.6), Inches(1.0), d, size=16, color=INK, name=f"Approach {i+1} text")
    tb(s, x + Inches(0.3), y0 + ch - Inches(0.55), cw - Inches(0.6), Inches(0.4), which, size=14, bold=True, color=MUTED, name=f"Approach {i+1} scope")
tb(s, Inches(0.7), Inches(6.85), Inches(12), Inches(0.35), "Data: multi-omics knowledge graph 0.1.0-alpha.9 · method reviewed by an independent critic · pilot on a draft pathway list",
   size=12, color=RGBColor(0x9F, 0xD4, 0xB2), name="Footnote")
s.notes_slide.notes_text_frame.text = "The question has two parts: can Prochlorococcus use amino acids for nitrogen, and do strains differ. My own growth experiments are not in the database; this work asks what genomes and existing expression experiments can tell."

# ================= Slide 2: results =================
s = prs.slides.add_slide(blank)
tb(s, Inches(0.7), Inches(0.4), Inches(12), Inches(0.7), "Results: MED4 and MIT9313 have almost no amino-acid machinery", size=30, font=HEAD, bold=True, name="Title")
pic = s.shapes.add_picture(str(FIG / "fig_aa_comparison_strip.png"), Inches(0.65), Inches(1.2), width=Inches(12.05)); pic.name = "Per-amino-acid breakdown strip"
y = Inches(1.2) + pic.height + Inches(0.25)
ch = H - y - Inches(0.55); cw, gap = Inches(3.88), Inches(0.2)
cards = [
    ("Breakdown pathways", PRO, PRO_L, [[("Complete pathways (of 20): ", {}), ("MED4 1", {"bold": True, "color": PRO}), (" · ", {}), ("MIT9313 2", {"bold": True, "color": PRO}), (" · ", {}), ("Alteromonas 8", {"bold": True, "color": HET}), (" · ", {}), ("E. coli ~10*", {"bold": True, "color": HET})],
                                        [("Every ", {}), ("Prochlorococcus", {"italic": True}), (" hit is a lone gene, never next to a transporter", {})]]),
    ("Uptake", PRO, PRO_L, [[("MED4: ", {"bold": True}), ("1 candidate amino-acid transporter (gltS)", {})],
                            [("E. coli: ", {"bold": True, "color": HET}), ("~25–30 systems*", {})],
                            [("MED4 keeps a full uptake + breakdown package for ", {}), ("urea", {"bold": True}), (", not amino acids", {})]]),
    ("MED4 experiments", UP, UP_L, [[("Short-term N deprivation: ", {"bold": True}), ("glnA, urea genes up (+5); ", {}), ("no amino-acid gene responds", {"bold": True})],
                                    [("Long-term starvation: ", {"bold": True}), ("peptide-binding dppA, ilvE, urease up → recycling own proteins / peptides?", {})]]),
]
for i, (h, colr, fill, paras) in enumerate(cards):
    x = Inches(0.7) + i * (cw + gap)
    box(s, x, y, cw, ch, fill, name=f"Result {i+1} card")
    tb(s, x + Inches(0.25), y + Inches(0.2), cw - Inches(0.5), Inches(0.45), h, size=20, bold=True, font=HEAD, color=colr, name=f"Result {i+1} title")
    tb(s, x + Inches(0.25), y + Inches(0.75), cw - Inches(0.5), ch - Inches(0.9), paras, size=15, after=10, name=f"Result {i+1} text")
tb(s, Inches(0.7), H - Inches(0.42), Inches(12), Inches(0.3), "* E. coli = textbook expectation; there is no E. coli genome in the database. Pilot on a draft pathway list; annotation ≠ proven function.", size=11, color=MUTED, name="Footnote")
s.notes_slide.notes_text_frame.text = ("Top: best breakdown pathway per amino acid. MED4 1 (Asn, PMM0821), MIT9313 2 (Asn PMT0825, Ala PMT1462), Alteromonas HOT1A3 8, E. coli ~10 expected. "
    "Uptake: MED4 gltS PMM0628 only; dppA PMM1049 binds peptides. Expression: glnA PMM0920 and urtA PMM0970 up strongly in Tolonen 2006 and Read 2017; gltS and asparaginase ns; "
    "in 2025 long-term starvation dppA, ilvE PMM0878 and urease up.")

# ================= Slide 3: conclusion =================
s = prs.slides.add_slide(blank)
tb(s, Inches(0.7), Inches(0.4), Inches(12), Inches(0.7), "Conclusion", size=34, font=HEAD, bold=True, name="Title")
box(s, Inches(0.7), Inches(1.25), Inches(11.93), Inches(1.35), PRO, name="Main message card")
tb(s, Inches(1.0), Inches(1.3), Inches(11.4), Inches(1.25),
   [[("The two ", {}), ("Prochlorococcus", {"italic": True}), (" strains studied do not look built to use free amino acids as a nitrogen source: almost no dedicated uptake or breakdown genes, and in MED4 they are not switched on when nitrogen is short.", {})]],
   size=21, bold=True, color=WHITE, font=HEAD, anchor=MSO_ANCHOR.MIDDLE, name="Main message")
pts = [("Genomes", "MED4 and MIT9313 carry 1–2 complete breakdown pathways vs 8–10 in heterotrophs; uptake is limited to one candidate gene in MED4.", PRO),
       ("Experiments", "Under N stress MED4 switches on ammonium and urea genes, not amino-acid genes.", UP),
       ("Alternative routes", "Peptides and recycling of its own proteins may be how organic N matters, rather than free amino acids.", UP)]
x0, y0, cw, ch, gap = Inches(0.7), Inches(2.9), Inches(3.85), Inches(2.0), Inches(0.19)
for i, (h, d, colr) in enumerate(pts):
    x = x0 + i * (cw + gap)
    box(s, x, y0, cw, ch, PANEL, name=f"Conclusion {i+1} card")
    num(s, x + Inches(0.25), y0 + Inches(0.25), i + 1, colr, f"Conclusion {i+1} number")
    tb(s, x + Inches(0.95), y0 + Inches(0.3), cw - Inches(1.15), Inches(0.5), h, size=20, bold=True, font=HEAD, color=colr, name=f"Conclusion {i+1} title")
    tb(s, x + Inches(0.25), y0 + Inches(0.95), cw - Inches(0.5), ch - Inches(1.05), d, size=15, name=f"Conclusion {i+1} text")
# open + next
box(s, Inches(0.7), Inches(5.15), Inches(6.85), Inches(1.75), WARN_L, name="Open card")
t = tb(s, Inches(0.95), Inches(5.3), Inches(6.4), Inches(1.5),
       [[("Not answered yet", {"bold": True, "color": WARN, "size": 18, "font": HEAD})],
        [("Do strains differ? Only 2 of 45 strains looked at", {})],
        [("Uptake when amino acids are present: not tested in these experiments", {})],
        [("Growth on amino acids as sole N: needs my experiments", {})]], size=15, after=4, name="Open text")
box(s, Inches(7.75), Inches(5.15), Inches(4.88), Inches(1.75), WHITE, line=PRO, name="Next card")
tb(s, Inches(8.0), Inches(5.3), Inches(4.4), Inches(1.5),
   [[("Next", {"bold": True, "color": PRO, "size": 18, "font": HEAD})],
    [("All 45 strains by amino-acid group, with uptake", {})],
    [("MIT9313 with amino-acid-rich lysate (expression)", {})],
    [("Put the genomes beside my growth data", {})]], size=15, after=4, name="Next text")
tb(s, Inches(0.7), H - Inches(0.42), Inches(12), Inches(0.3), "Interpretation from genome annotations and expression data; pilot results not yet independently reviewed. KG 0.1.0-alpha.9.", size=11, color=MUTED, name="Footnote")
s.notes_slide.notes_text_frame.text = "The answer so far is about capacity and regulation, not proof of use. The strain-difference half of the question and actual growth on amino acids remain open; my growth experiments are the missing piece."

prs.save(out); print("saved", out, len(prs.slides), "slides")
