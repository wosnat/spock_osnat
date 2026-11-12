"""Spike: one-slide (1920x1080) infographic, MED4 vs HOT1A3 gene counts per role, from the gene tables.
All numbers and callout text are computed from data/*.csv here; no KG calls.
Run (repo root): PYTHONUTF8=1 uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s04_infographic.py
Then render: chrome --headless --screenshot (see run manifest).
"""
import html
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, REP = ROOT / "data", ROOT / "reports"
COL = {"MED4": "#6250d6", "HOT1A3": "#0b8aa6"}  # validated all-pairs, light surface #fcfcfb
ORGS = ["MED4", "HOT1A3"]

df = pd.concat([pd.read_csv(DATA / f"{t}_aa_peptide_gene_table.csv", encoding="utf-8", keep_default_na=False)
                for t in ("med4", "hot1a3")], ignore_index=True)
genome = json.loads((DATA / "genome_gene_counts.json").read_text(encoding="utf-8"))
subr = pd.read_csv(DATA / "med4_vs_hot1a3_subroles.csv", encoding="utf-8", keep_default_na=False)
strong = df[df.weak_evidence_only == "no"]

def explode(d, col):
    e = d.assign(**{col: d[col].str.split(r" \| ")}).explode(col)
    e[col] = e[col].str.strip()
    return e

def counts(d, role, col, order=None, drop_prefix=None):
    e = explode(d[d.role == role], col)
    if drop_prefix:
        e = e[~e[col].str.startswith(drop_prefix)]
    c = e.groupby([col, "organism"]).locus_tag.nunique().unstack("organism", fill_value=0)
    for o in ORGS:
        if o not in c:
            c[o] = 0
    c = c[ORGS]
    if order:
        c = c.reindex([x for x in order if x in c.index])
    else:
        c = c.loc[c.sum(axis=1).sort_values(ascending=False).index]
    return c

AA_ORDER = ["peptides", "small (Gly/Ala/Ser)", "polar/neutral", "hydrophobic/branched-chain", "aromatic",
            "sulfur", "basic", "acidic", "amides (Asn/Gln)", "broad/unknown"]
up = counts(strong[~strong.subrole.str.contains("protein translocation")], "uptake", "aa_class", AA_ORDER)
ne = counts(strong, "N-entry enzyme", "aa_class", AA_ORDER)
pe = counts(strong, "peptidase", "subrole")
pe = pe.rename(index={"housekeeping protease (by product keyword)": "housekeeping (by keyword)",
                      "peptidase (EC sub-subclass not stated)": "no EC sub-subclass"})
pe = pe.head(10)
core = counts(strong, "N-assimilation core", "subrole")

def panel(title, note, c):
    vmax = max(1, int(c.values.max()))
    rows = []
    for k, r in c.iterrows():
        bars = ""
        for o in ORGS:
            v = int(r[o])
            w = 0 if v == 0 else max(0.6, 100 * v / vmax)
            bars += (f"<div class='bar' title='{o}: {v} genes'><i style='width:{w:.1f}%;background:{COL[o]}'></i>"
                     f"<span>{v}</span></div>")
        rows.append(f"<div class='row'><div class='lab'>{html.escape(k)}</div><div class='bars'>{bars}</div></div>")
    return (f"<section><h2>{html.escape(title)}</h2><p class='pn'>{html.escape(note)}</p>"
            f"<div class='rows'>{''.join(rows)}</div></section>")

# ---- callouts (all from data) ----
pu = strong[(strong.role == "uptake") & strong.aa_class.str.contains("peptides")
            & ~strong.subrole.str.contains("protein translocation")]
pu_n = {o: pu[pu.organism == o].locus_tag.nunique() for o in ORGS}
aa_up = explode(strong[(strong.role == "uptake") & ~strong.subrole.str.contains("protein translocation")], "aa_class")
aa_up = aa_up[~aa_up.aa_class.isin(["peptides", "broad/unknown"])]
m_cls = aa_up[aa_up.organism == "MED4"].groupby("aa_class").locus_tag.apply(lambda s: sorted(set(s)))
h_cls = aa_up[aa_up.organism == "HOT1A3"].aa_class.nunique()
m_txt = "; ".join(f"{k}: {', '.join(v)}" for k, v in m_cls.items())
urt_flag = any(lt in {"PMM0970", "PMM0971", "PMM0972", "PMM0973", "PMM0974"} for v in m_cls for lt in v)
ne_cat = subr[(subr.role == "N-entry enzyme") & subr.subrole.str.startswith("catalogue step")]
cat_h_only = int((ne_cat.present_in == "HOT1A3 only").sum())
cat_m_only = int((ne_cat.present_in == "MED4 only").sum())
cat_both = int((ne_cat.present_in == "both").sum())
callouts = [
    f"<b>Peptide uptake</b> (ABC PepT family, peptide GO/TCDB terms; weak-only and Sec/Tat rows removed): "
    f"<b>{pu_n['MED4']}</b> genes in MED4 vs <b>{pu_n['HOT1A3']}</b> in HOT1A3. MED4: "
    + html.escape(", ".join(f"{r.locus_tag} {r.gene_name or '(no name)'}" for r in pu[pu.organism == 'MED4'].drop_duplicates('locus_tag').itertuples())),
    f"<b>Amino-acid uptake</b> genes cover <b>{m_cls.size}</b> of 8 amino-acid classes in MED4 vs <b>{h_cls}</b> in HOT1A3. "
    f"MED4 genes: {html.escape(m_txt)}"
    + (" — urtA–E (PMM0970–0974) are placed by TCDB as a urea porter." if urt_flag else ""),
    f"<b>Prior-catalogue enzyme steps</b> found: <b>{cat_both}</b> in both, <b>{cat_h_only}</b> only in HOT1A3, "
    f"<b>{cat_m_only}</b> only in MED4.",
]

gm, gh = genome["MED4"]["gene_count"], genome["HOT1A3"]["gene_count"]
tot = {o: strong[strong.organism == o].locus_tag.nunique() for o in ORGS}
page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Amino-acid and peptide use genes: MED4 vs HOT1A3 (spike draft)</title>
<style>
:root{{--ink:#1f2328;--muted:#59636e;--line:#d0d7de;--bg:#fcfcfb;--panel:#f3f4f6;--m:{COL['MED4']};--h:{COL['HOT1A3']}}}
*{{box-sizing:border-box}} html,body{{margin:0;background:#e9eaec}}
.slide{{width:1920px;height:1080px;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
 padding:34px 56px 22px;display:grid;grid-template-rows:auto 1fr auto auto;gap:14px;overflow:hidden}}
h1{{margin:0;font-size:38px;line-height:1.1}} .sub{{margin:6px 0 0;font-size:19px;color:var(--muted)}}
.leg{{display:flex;gap:30px;margin-top:10px;font-size:20px}} .leg span{{display:flex;align-items:center;gap:8px}}
.leg i{{width:26px;height:14px;border-radius:3px;display:inline-block}}
.tag{{display:inline-block;font-size:15px;font-weight:600;border:1.5px solid #eda100;color:#9a6700;border-radius:14px;padding:2px 12px;margin-left:12px;vertical-align:6px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:10px 40px;min-height:0}}
section{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 18px;min-height:0;overflow:hidden}}
h2{{margin:0;font-size:22px}} .pn{{margin:2px 0 6px;font-size:14px;color:var(--muted)}}
.row{{display:grid;grid-template-columns:260px 1fr;align-items:center;gap:10px;margin:2px 0}}
.lab{{font-size:15px;text-align:right;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.bars{{display:grid;gap:2px}} .bar{{display:flex;align-items:center;gap:6px;height:11px}}
.bar i{{display:block;height:11px;border-radius:0 4px 4px 0}} .bar span{{font-size:12px;color:var(--muted);line-height:1}}
.call{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.call div{{background:var(--panel);border-radius:10px;padding:8px 14px;font-size:15.5px;line-height:1.3}}
.foot{{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:6px}}
</style></head><body><div class="slide">
<div>
 <h1>Genes for using amino acids and peptides: <i>Prochlorococcus</i> MED4 vs <i>Alteromonas</i> HOT1A3 <span class="tag">draft, genome only</span></h1>
 <p class="sub">MED4 genome <b>{gm:,}</b> genes · HOT1A3 genome <b>{gh:,}</b> genes (KG). Genes in the table (weak-evidence-only rows removed): MED4 <b>{tot['MED4']}</b>, HOT1A3 <b>{tot['HOT1A3']}</b>. Bars = number of distinct genes; a gene with several classes counts in each.</p>
 <div class="leg"><span><i style="background:var(--m)"></i>MED4</span><span><i style="background:var(--h)"></i>HOT1A3</span></div>
</div>
<div class="grid">
 {panel("Uptake — by amino-acid class", "TCDB systems/families, GO transporter terms, SBP predictions; Sec/Tat translocases and family-walk-only rows removed", up)}
 {panel("Enzymes acting on amino acids — by class", "aminotransferases, AA dehydrogenases/oxidases, amidohydrolases, ammonia-lyases, decarboxylases, glycine cleavage, prior-catalogue KOs", ne)}
 {panel("Peptidases — by type (top 10)", "EC 3.4.*, MEROPS peptidase calls, GO peptidase terms (GO-only rows removed); 'housekeeping' = product keyword (Clp, FtsH, signal peptidase…)", pe)}
 {panel("Nitrogen assimilation core — by enzyme", "KEGG KOs: glutamine synthetase, GOGAT, GDH, urease, ammonium transporter, asparagine synthetase", core)}
</div>
<div class="call">{''.join(f'<div>{c}</div>' for c in callouts)}</div>
<div class="foot">Source: spike tables data/med4_aa_peptide_gene_table.csv and data/hot1a3_aa_peptide_gene_table.csv (multiomics KG 0.1.0-alpha.9). Class labels come from substrate words in the annotation; counts describe annotation, not activity.</div>
</div></body></html>"""
out = REP / "med4_vs_hot1a3_infographic.html"
out.write_text(page, encoding="utf-8")
print(out)
for c in callouts:
    print("CALLOUT:", c)
print(up, ne, pe, core, sep="\n")
