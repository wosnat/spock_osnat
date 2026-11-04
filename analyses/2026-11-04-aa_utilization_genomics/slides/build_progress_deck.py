"""Build a 5-slide progress deck for the amino-acid utilization analysis.

Usage: python build_deck.py <analysis_root> <out.pptx>
"""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

root = Path(sys.argv[1]); out = Path(sys.argv[2])
INK = RGBColor(0x1F, 0x23, 0x28); MUTED = RGBColor(0x59, 0x63, 0x6E)
VIOLET = RGBColor(0x62, 0x50, 0xD6); VIOLET_L = RGBColor(0xEF, 0xED, 0xFB)
DARK = RGBColor(0x1B, 0x1A, 0x3A); WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PANEL = RGBColor(0xF3, 0xF4, 0xF6); GREEN = RGBColor(0x0D, 0x7A, 0x54)
HEAD, BODY = "Cambria", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]
W, H = prs.slide_width, prs.slide_height

def text(slide, x, y, w, h, runs, size=16, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name=None):
    tb = slide.shapes.add_textbox(x, y, w, h)
    if name: tb.name = name
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = runs if isinstance(runs, list) else [runs]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        segs = p if isinstance(p, list) else [(p, {})] if isinstance(p, str) else [p]
        for seg, opt in segs:
            r = para.add_run(); r.text = seg
            r.font.size = Pt(opt.get("size", size)); r.font.name = opt.get("font", font)
            r.font.bold = opt.get("bold", bold); r.font.italic = opt.get("italic", False)
            r.font.color.rgb = opt.get("color", color)
        para.space_after = Pt(opt.get("after", 6) if segs else 6)
    return tb

def card(slide, x, y, w, h, fill=PANEL, line=None, name=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    s.adjustments[0] = 0.06
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None: s.line.fill.background()
    else: s.line.color.rgb = line; s.line.width = Pt(1.75)
    s.shadow.inherit = False
    if name: s.name = name
    return s

def image_slide(img, notes, name):
    s = prs.slides.add_slide(blank)
    p = s.shapes.add_picture(str(img), 0, 0, width=W, height=H)
    p.name = name
    s.shapes.title if False else None
    s.notes_slide.notes_text_frame.text = notes
    return s

# ---------- Slide 1: question + what was done (dark) ----------
s = prs.slides.add_slide(blank)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H); bg.fill.solid(); bg.fill.fore_color.rgb = DARK; bg.line.fill.background(); bg.name = "Background"
text(s, Inches(0.7), Inches(0.55), Inches(12), Inches(0.9),
     [[("Amino-acid utilization in ", {}), ("Prochlorococcus", {"italic": True})]],
     size=38, color=WHITE, font=HEAD, bold=True, name="Title")
text(s, Inches(0.7), Inches(1.45), Inches(12), Inches(0.4),
     "Progress so far  ·  comparative genomics with the lab knowledge graph  ·  Dikla Aharonovich  ·  4 Nov 2026", size=16, color=RGBColor(0xC9, 0xC6, 0xF2), name="Subtitle")
# question card
card(s, Inches(0.7), Inches(2.15), Inches(11.93), Inches(1.55), fill=RGBColor(0x2A, 0x28, 0x55), name="Question card")
text(s, Inches(1.0), Inches(2.3), Inches(11.4), Inches(1.3),
     [[("THE QUESTION", {"size": 13, "bold": True, "color": RGBColor(0x9F, 0x95, 0xF0)})],
      [("For each of the 20 amino acids, which ", {}), ("Prochlorococcus", {"italic": True}),
       (" strains carry a breakdown pathway that frees its nitrogen, judged only by enzymes used solely for breakdown? How does this differ between clades and from marine ", {}),
       ("Synechococcus", {"italic": True}), ("?", {})]],
     size=20, color=WHITE, name="Question text")
# progress steps
steps = [("1", "Question & plan", "Database checked; plan reviewed 3× by an independent critic; approved"),
         ("2", "MED4 pilot", "1 of 34 breakdown-only enzymes found (asparaginase)"),
         ("3", "Pathway list", "58 pathways for 20 amino acids; 3 review rounds; awaiting your approval"),
         ("4", "Comparisons", "Alteromonas HOT1A3: 8 complete pathways vs MED4's 1; MIT9313 running")]
x0, y0, cw, ch, gap = Inches(0.7), Inches(4.15), Inches(2.84), Inches(2.55), Inches(0.19)
for i, (n, h, d) in enumerate(steps):
    x = x0 + i * (cw + gap)
    card(s, x, y0, cw, ch, fill=WHITE, name=f"Step {n} card")
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.25), y0 + Inches(0.25), Inches(0.55), Inches(0.55))
    c.fill.solid(); c.fill.fore_color.rgb = VIOLET; c.line.fill.background(); c.name = f"Step {n} badge"
    c.text_frame.text = n; c.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    r = c.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = BODY
    c.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    text(s, x + Inches(0.25), y0 + Inches(0.95), cw - Inches(0.5), Inches(0.45), h, size=19, bold=True, color=INK, font=HEAD, name=f"Step {n} title")
    text(s, x + Inches(0.25), y0 + Inches(1.45), cw - Inches(0.5), Inches(1.0), d, size=15, color=MUTED, name=f"Step {n} text")
s.notes_slide.notes_text_frame.text = (
    "Standalone comparative-genomics question; no hypothesis going in. My own amino-acid growth experiments are not in the database and are not part of this analysis. "
    "Transporters (uptake) were set aside after the MED4 pilot. Data: multi-omics KG release 0.1.0-alpha.9.")

# ---------- Slides 2-4: infographics ----------
image_slide(root / "slides/heterotroph_vs_prochlorococcus_general_slide.png",
    "Framing. For a heterotroph an amino acid is food (carbon, energy, nitrogen); for a photoautotroph it can only offer nitrogen or a ready-made building block. "
    "Genus-wide numbers from the database: 1,870–3,203 genes and 32–81 transported compounds per strain. Everything tagged 'background' is general knowledge to be cited before publication.",
    "General comparison infographic")
image_slide(root / "spike/figures/med4_pilot_slide.png",
    "MED4 pilot (draft enzyme list). Only asparaginase (PMM0821) is a breakdown-only enzyme; 12 amino acids have only shared enzymes, 7 nothing. "
    "Lessons that shaped the plan: transporters set aside, score whole pathways on breakdown-only steps, match by enzyme ID not gene name.",
    "MED4 pilot infographic")
image_slide(root / "spike/alteromonas_hot1a3/figures/hot1a3_vs_med4_slide.png",
    "Same draft pathway list and rules on the marine heterotroph Alteromonas HOT1A3: 8 complete pathways vs MED4's 1; 14 vs 1 breakdown-only steps found. "
    "Shows the method can find complete pathways where they exist. Caveats: HOT1A3 genome is ~2x larger; keyword synonyms (e.g. glnA 'glutamate--ammonia ligase') still to fix.",
    "MED4 vs Alteromonas infographic")

# ---------- Slide 5: status & next steps ----------
s = prs.slides.add_slide(blank)
text(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.8), "Where we are and what comes next", size=36, font=HEAD, bold=True, name="Title")
cols = [
    ("What we learned", VIOLET, [
        "MED4 has almost no breakdown-only machinery: 1 enzyme, a lone gene",
        "MED4 keeps a full uptake + breakdown package for urea, not for amino acids",
        "The method does find complete pathways in a heterotroph (Alteromonas: 8)",
        "Some amino acids can't be judged with this database: Gly, Glu, Tyr"]),
    ("Decisions for you", GREEN, [
        "Approve the pathway list (23 debatable steps, 2 additions, controls)",
        "Bring Alteromonas back as a reference group?",
        "Keep the operon (gene-neighbourhood) check?",
        "Add other annotation types (A) and/or transporters (B)?"]),
    ("Next steps", INK, [
        "MIT9313 pilot (low-light) — running",
        "Fix keyword synonyms; choose a new blind check strain",
        "Score all 45 Prochlorococcus + marine Synechococcus",
        "Heatmap by clade, reports, paper-ready text"]),
]
cx, cy, cw2, ch2, g2 = Inches(0.7), Inches(1.6), Inches(3.84), Inches(5.2), Inches(0.24)
for i, (h, colr, items) in enumerate(cols):
    x = cx + i * (cw2 + g2)
    card(s, x, cy, cw2, ch2, fill=PANEL, name=f"{h} card")
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.3), cy + Inches(0.32), Inches(0.32), Inches(0.32))
    dot.fill.solid(); dot.fill.fore_color.rgb = colr; dot.line.fill.background(); dot.name = f"{h} marker"
    text(s, x + Inches(0.75), cy + Inches(0.25), cw2 - Inches(1.0), Inches(0.5), h, size=22, bold=True, font=HEAD, color=colr, name=f"{h} header")
    tb = text(s, x + Inches(0.3), cy + Inches(1.0), cw2 - Inches(0.6), ch2 - Inches(1.2), [[(t, {"after": 12})] for t in items], size=16, name=f"{h} list")
    for p in tb.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Emu(Inches(0.25)))); pPr.set("indent", str(-Emu(Inches(0.25))))
        from pptx.oxml.ns import qn
        from lxml import etree
        bu = etree.SubElement(pPr, qn("a:buChar")); bu.set("char", "•")
        p.space_after = Pt(12)
text(s, Inches(0.7), Inches(6.95), Inches(12), Inches(0.35),
     "Pilot results use a draft pathway list (not yet approved). Annotation ≠ proven function. KG 0.1.0-alpha.9.", size=11, color=MUTED, name="Footnote")
s.notes_slide.notes_text_frame.text = "Decisions needed before scoring all strains. MIT9313 was unblinded for the pilot at my request; a replacement blind low-light strain will be chosen before approving the list."

prs.save(out)
print("saved", out, len(prs.slides), "slides")
