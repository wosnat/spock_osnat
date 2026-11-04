"""Three-slide summary: what I asked, what I did, what I got (and why the question is still open).

Usage: python build_three_slide_deck.py <out.pptx>
Numbers come from the pilot data files (spike/*/data/*.csv), verified in methods/notebook.md.
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

out = sys.argv[1]
INK = RGBColor(0x1F, 0x23, 0x28); MUTED = RGBColor(0x59, 0x63, 0x6E)
PRO = RGBColor(0x1F, 0x8A, 0x4C); PRO_L = RGBColor(0xE5, 0xF4, 0xEA)
HET = RGBColor(0x1D, 0x5F, 0xAE); HET_L = RGBColor(0xE6, 0xEE, 0xF9)
DARK = RGBColor(0x12, 0x2B, 0x1E); WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PANEL = RGBColor(0xF3, 0xF4, 0xF6); WARN = RGBColor(0x9A, 0x67, 0x00); WARN_L = RGBColor(0xFD, 0xF3, 0xDC)
HEAD, BODY = "Cambria", "Calibri"

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
W, H = prs.slide_width, prs.slide_height
blank = prs.slide_layouts[6]

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

def bullets(t, indent=0.28):
    from pptx.oxml.ns import qn
    from lxml import etree
    from pptx.util import Emu
    for p in t.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Emu(Inches(indent)))); pPr.set("indent", str(-Emu(Inches(indent))))
        bu = etree.SubElement(pPr, qn("a:buChar")); bu.set("char", "•")

def title(s, text, sub=None, dark=False):
    tb(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.8), [[(t, o) for t, o in text]], size=38, font=HEAD, bold=True, color=(WHITE if dark else INK), name="Title")
    if sub:
        tb(s, Inches(0.7), Inches(1.3), Inches(12), Inches(0.45), sub, size=18, color=(RGBColor(0xB9, 0xE3, 0xC8) if dark else MUTED), name="Subtitle")

# ---------------- Slide 1: what I asked ----------------
s = prs.slides.add_slide(blank)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H); bg.fill.solid(); bg.fill.fore_color.rgb = DARK; bg.line.fill.background(); bg.name = "Background"
title(s, [("1 · What I asked", {})], "Dikla Aharonovich · amino-acid utilization in Prochlorococcus · 4 Nov 2026", dark=True)
box(s, Inches(0.7), Inches(2.0), Inches(11.93), Inches(1.75), RGBColor(0x1E, 0x45, 0x30), name="Question card")
tb(s, Inches(1.05), Inches(2.2), Inches(11.3), Inches(1.4),
   [[("Can ", {}), ("Prochlorococcus", {"italic": True}), (" use amino acids as a nitrogen source, and do strains differ in this ability?", {})]],
   size=30, font=HEAD, bold=True, color=WHITE, name="Question", anchor=MSO_ANCHOR.MIDDLE)
# three sub-questions as a flow
steps = [("Take it up?", "Does the genome carry amino-acid transporters?"),
         ("Break it down?", "Does it carry enzymes that free the nitrogen?"),
         ("Strains differ?", "High-light vs low-light clades; vs Synechococcus")]
x0, y0, cw, ch, gap = Inches(0.7), Inches(4.25), Inches(3.75), Inches(1.75), Inches(0.34)
for i, (h, d) in enumerate(steps):
    x = x0 + i * (cw + gap)
    box(s, x, y0, cw, ch, WHITE, name=f"Sub-question {i+1}")
    c = box(s, x + Inches(0.25), y0 + Inches(0.3), Inches(0.6), Inches(0.6), PRO, shape=MSO_SHAPE.OVAL, name=f"Number {i+1}")
    c.text_frame.text = str(i + 1); p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.runs[0]; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = BODY; c.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    tb(s, x + Inches(1.05), y0 + Inches(0.3), cw - Inches(1.3), Inches(0.5), h, size=22, bold=True, font=HEAD, color=PRO, name=f"Sub-question {i+1} title")
    tb(s, x + Inches(1.05), y0 + Inches(0.9), cw - Inches(1.3), Inches(0.8), d, size=16, color=MUTED, name=f"Sub-question {i+1} text")
    if i < 2:
        a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + cw + Inches(0.05), y0 + ch / 2 - Inches(0.15), gap - Inches(0.1), Inches(0.3))
        a.fill.solid(); a.fill.fore_color.rgb = RGBColor(0x7F, 0xB8, 0x95); a.line.fill.background(); a.name = f"Arrow {i+1}"
tb(s, Inches(0.7), Inches(6.45), Inches(11.9), Inches(0.6),
   "Starting point: my growth experiments with several strains on amino acids as the only N source. They are not in the lab database, so this analysis asks what the genomes allow.",
   size=16, color=RGBColor(0xB9, 0xE3, 0xC8), name="Starting point")
s.notes_slide.notes_text_frame.text = "The question has two parts: capacity (uptake + breakdown genes) and differences between strains/clades. The database holds 45 Prochlorococcus genomes but no amino-acid growth experiments."

# ---------------- Slide 2: what I did ----------------
s = prs.slides.add_slide(blank)
title(s, [("2 · What I did", {})], "Comparative genomics with the lab knowledge graph: build a method, test it on a few genomes first")
cards = [
    ("Checked the database", "45 Prochlorococcus genomes, all clades; no amino-acid growth experiments", PRO),
    ("Built a pathway list", "58 breakdown pathways for 20 amino acids; only breakdown-only steps count; reviewed 3×", PRO),
    ("Ran pilots", "Same list and rules on MED4 (high-light), MIT9313 (low-light) and the heterotroph Alteromonas HOT1A3", PRO),
    ("Heterotroph comparison", "Uptake and breakdown vs E. coli (textbook) and Alteromonas (database)", HET),
    ("Checked gene neighbours", "Is a breakdown gene next to a transporter (an uptake + breakdown package)?", PRO),
]
x0, y0, cw, ch, gap = Inches(0.7), Inches(1.95), Inches(2.25), Inches(3.6), Inches(0.17)
for i, (h, d, colr) in enumerate(cards):
    x = x0 + i * (cw + gap)
    box(s, x, y0, cw, ch, (HET_L if colr == HET else PRO_L), name=f"Step {i+1} card")
    c = box(s, x + Inches(0.22), y0 + Inches(0.25), Inches(0.55), Inches(0.55), colr, shape=MSO_SHAPE.OVAL, name=f"Step {i+1} number")
    c.text_frame.text = str(i + 1); p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.runs[0]; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = BODY; c.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    tb(s, x + Inches(0.22), y0 + Inches(0.95), cw - Inches(0.4), Inches(0.8), h, size=18, bold=True, font=HEAD, color=colr, name=f"Step {i+1} title")
    tb(s, x + Inches(0.22), y0 + Inches(1.85), cw - Inches(0.4), ch - Inches(2.0), d, size=15, color=INK, name=f"Step {i+1} text")
# how the question was narrowed
box(s, Inches(0.7), Inches(5.75), Inches(11.93), Inches(1.15), PANEL, name="Decisions card")
tb(s, Inches(1.0), Inches(5.9), Inches(11.4), Inches(0.9),
   [[("Decisions along the way: ", {"bold": True}),
     ("focus on nitrogen · transporters set aside after MED4 (now coming back) · score whole pathways, ignore enzymes that also build amino acids · match genes by enzyme ID, not name · each change re-checked by an independent reviewer", {})]],
   size=16, name="Decisions text")
s.notes_slide.notes_text_frame.text = "All analysis steps are scripted and saved in git. MIT9313 was unblinded for the pilot at my request; a different low-light strain will serve as the blind check."

# ---------------- Slide 3: what I got / why not answered yet ----------------
s = prs.slides.add_slide(blank)
tb(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.8), "3 · What I got, and why I can't answer the question yet", size=32, font=HEAD, bold=True, name="Title")
# left: results
box(s, Inches(0.7), Inches(1.55), Inches(6.3), Inches(5.35), PANEL, name="Results card")
tb(s, Inches(1.0), Inches(1.75), Inches(5.8), Inches(0.5), "What I got (pilot, draft pathway list)", size=21, bold=True, font=HEAD, name="Results header")
stats = [("1", "MED4", "complete breakdown pathway (Asn)", PRO), ("2", "MIT9313", "complete (Asn, Ala)", PRO),
         ("8", "Alteromonas", "complete (database)", HET), ("~10", "E. coli", "expected (textbook)", HET)]
for i, (n, org, lab, colr) in enumerate(stats):
    x = Inches(1.0) + (i % 2) * Inches(2.95); y = Inches(2.4) + (i // 2) * Inches(1.25)
    tb(s, x, y, Inches(1.1), Inches(0.9), n, size=44, bold=True, color=colr, name=f"Stat {org} number", anchor=MSO_ANCHOR.MIDDLE)
    tb(s, x + Inches(1.15), y + Inches(0.12), Inches(1.75), Inches(0.9), [[(org, {"bold": True, "color": colr})], [(lab, {"size": 13, "color": MUTED})]], size=16, name=f"Stat {org} label", after=2)
t = tb(s, Inches(1.0), Inches(4.95), Inches(5.8), Inches(1.9),
       [[("Uptake: MED4 has ", {}), ("1 candidate", {"bold": True}), (" amino-acid transporter (gltS) vs ~25–30 systems in E. coli", {})],
        [("Every ", {}), ("Prochlorococcus", {"italic": True}), (" breakdown gene is a ", {}), ("lone gene", {"bold": True}), ("; Alteromonas has uptake + breakdown packages", {})],
        [("MED4 keeps such a package for urea, not for amino acids", {})]], size=15, after=8, name="Results bullets")
bullets(t)
# right: why not answered
box(s, Inches(7.25), Inches(1.55), Inches(5.38), Inches(5.35), WARN_L, name="Open card")
tb(s, Inches(7.55), Inches(1.75), Inches(4.9), Inches(0.5), "Why the question is still open", size=21, bold=True, font=HEAD, color=WARN, name="Open header")
t = tb(s, Inches(7.55), Inches(2.4), Inches(4.85), Inches(3.3),
       [[("Genes ≠ use. ", {"bold": True}), ("Cells can build amino acids straight into protein without breaking them down", {})],
        [("Only 2 of 45 strains looked at so far ", {"bold": True}), ("(MED4, MIT9313); no clade comparison yet", {})],
        [("Uptake checked only in MED4. ", {"bold": True}), ("Low-light strains may carry transporters MED4 lacks", {})],
        [("Blind spots: ", {"bold": True}), ("Gly, Glu, Tyr can't be judged; the pathway list is still a draft", {})],
        [("No growth data in the database. ", {"bold": True}), ("Growth on amino acids as the only N source may not be published", {})]],
       size=15, after=9, name="Open bullets")
bullets(t)
box(s, Inches(7.55), Inches(5.85), Inches(4.8), Inches(0.85), WHITE, line=PRO, name="Next card")
tb(s, Inches(7.75), Inches(5.95), Inches(4.45), Inches(0.7),
   [[("Next: ", {"bold": True, "color": PRO}), ("approve the list, score all 45 strains by amino-acid group, add uptake, and set the genomes beside my growth experiments", {})]],
   size=14, name="Next text", anchor=MSO_ANCHOR.MIDDLE)
tb(s, Inches(0.7), Inches(7.0), Inches(12), Inches(0.3),
   "Pilot results on a draft pathway list. E. coli values are textbook expectations (no E. coli genome in the database). Annotation ≠ proven function. KG 0.1.0-alpha.9.",
   size=11, color=MUTED, name="Footnote")
s.notes_slide.notes_text_frame.text = ("Complete breakdown pathways: MED4 1 (asparaginase PMM0821), MIT9313 2 (asparaginase PMT0825, alanine dehydrogenase PMT1462), Alteromonas HOT1A3 8, E. coli ~10 expected (textbook). "
    "The genome analysis can only show capacity. Whether Prochlorococcus uses amino acids as an N source needs uptake evidence across strains, expression data, and growth experiments like mine.")

prs.save(out)
print("saved", out, len(prs.slides), "slides")
