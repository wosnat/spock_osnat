"""Spike: self-contained sortable/filterable HTML gene table (MED4 + HOT1A3) with count summaries.
Run (repo root): PYTHONUTF8=1 uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s03_report.py
"""
import html
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, REP = ROOT / "data", ROOT / "reports"
REP.mkdir(exist_ok=True)
COL = {"MED4": "#6250d6", "HOT1A3": "#0b8aa6"}  # validated: validate_palette.py --pairs all, light: all pass

tabs = [pd.read_csv(DATA / f"{t}_aa_peptide_gene_table.csv", encoding="utf-8", keep_default_na=False)
        for t in ("med4", "hot1a3")]
df = pd.concat(tabs, ignore_index=True)
counts = pd.read_csv(DATA / "med4_vs_hot1a3_counts.csv", encoding="utf-8", keep_default_na=False)
totals = pd.read_csv(DATA / "med4_vs_hot1a3_role_totals.csv", encoding="utf-8", keep_default_na=False)
subr = pd.read_csv(DATA / "med4_vs_hot1a3_subroles.csv", encoding="utf-8", keep_default_na=False)
genome = json.loads((DATA / "genome_gene_counts.json").read_text(encoding="utf-8"))

def table(d, cls="", tid=None):
    h = "".join(f"<th>{html.escape(str(c))}</th>" for c in d.columns)
    rows = []
    for _, r in d.iterrows():
        cells = "".join(f"<td>{html.escape(str(v))}</td>" for v in r.values)
        rows.append(f"<tr data-org='{html.escape(str(r.get('organism', '')))}'>{cells}</tr>")
    return f"<table class='{cls}' {'id=' + repr(tid) if tid else ''}><thead><tr>{h}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

COLS = ["organism", "role", "subrole", "aa_class", "locus_tag", "gene_name", "product", "substrates_stated",
        "evidence_sources", "weak_evidence_only", "evidence_quality", "shared_with_biosynthesis [interpretation]",
        "n_neighbours_in_table", "operon_neighbours", "ko", "ec", "evidence", "notes"]
roles = list(dict.fromkeys(df.role))
classes = sorted({c.strip() for v in df.aa_class for c in v.split("|")})
opt = lambda xs: "".join(f"<option>{html.escape(x)}</option>" for x in xs)  # noqa: E731

hdr = " · ".join(f"<span class='org' style='--c:{COL[o]}'>{html.escape(g['organism_name'])}</span>: "
                 f"<b>{g['gene_count']:,}</b> genes in genome, <b>{df[df.organism == o].locus_tag.nunique()}</b> "
                 f"in this table ({(df.organism == o).sum()} rows)" for o, g in genome.items())

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Amino-acid and peptide utilization genes: MED4 and HOT1A3 (spike draft)</title>
<style>
:root{{--ink:#1f2328;--muted:#59636e;--line:#d0d7de;--bg:#fcfcfb;--panel:#f3f4f6}}
body{{margin:0;padding:24px 32px;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}}
h1{{font-size:24px;margin:0 0 6px}} h2{{font-size:18px;margin:26px 0 8px}}
.sub{{color:var(--muted);margin:0 0 10px}} .org{{font-weight:700;border-left:5px solid var(--c);padding-left:6px}}
.warn{{background:#fff8e6;border:1px solid #eda100;border-radius:8px;padding:8px 12px;margin:10px 0;max-width:1300px}}
table{{border-collapse:collapse;font-size:12.5px}} th,td{{border-bottom:1px solid var(--line);padding:4px 7px;text-align:left;vertical-align:top}}
th{{position:sticky;top:0;background:#eef0f2;cursor:pointer;white-space:nowrap}} th:hover{{background:#e1e4e8}}
.small td{{white-space:nowrap}} .grid{{display:flex;gap:30px;flex-wrap:wrap;align-items:flex-start}}
#main td{{max-width:340px;overflow-wrap:anywhere}} #main td:nth-child(5){{font-family:ui-monospace,Consolas,monospace;white-space:nowrap}}
tr[data-org=MED4] td:first-child{{border-left:4px solid {COL['MED4']}}} tr[data-org=HOT1A3] td:first-child{{border-left:4px solid {COL['HOT1A3']}}}
.ctl{{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:8px 0;position:sticky;top:0;background:var(--bg);padding:6px 0;z-index:2}}
.ctl select,.ctl input{{font:inherit;padding:3px 6px}} #n{{color:var(--muted)}}
.wrap{{max-height:75vh;overflow:auto;border:1px solid var(--line)}}
</style></head><body>
<h1>Amino-acid and peptide utilization genes — <i>Prochlorococcus</i> MED4 and <i>Alteromonas macleodii</i> HOT1A3</h1>
<p class="sub">Spike draft (not reviewed). One row per (locus tag, role). {hdr}</p>
<div class="warn">How to read: membership comes from ontology ids / KG routes (TCDB, GO, EC, MEROPS, KEGG KO, SBP metric), never from product text.
Product text is used only to <i>label</i> rows (aa_class keywords, housekeeping / protein-translocation subroles).
<b>weak_evidence_only</b> = "yes" marks uptake rows supported only by a TCDB family-walk, and peptidase rows supported only by a GO term.
The <b>shared_with_biosynthesis</b> column is [interpretation] (rule-based, see notes per row). aa_class "peptides" is assigned to every peptidase.</div>

<h2>Gene counts per role (unique genes)</h2>
<div class="grid">{table(totals, 'small')}</div>
<h2>Gene counts per role × aa_class (a gene with several classes counts once in each)</h2>
<div class="grid">{table(counts, 'small')}</div>
<h2>Subrole categories: present in one genome or both</h2>
<div class="grid">{table(subr, 'small')}</div>

<h2>Gene table</h2>
<div class="ctl">
 <label>organism <select id="fo"><option value="">all</option>{opt(genome.keys())}</select></label>
 <label>role <select id="fr"><option value="">all</option>{opt(roles)}</select></label>
 <label>aa_class <select id="fc"><option value="">all</option>{opt(classes)}</select></label>
 <label><input type="checkbox" id="fw"> hide weak-evidence-only rows</label>
 <label>text <input id="ft" placeholder="locus tag, name, product…" size="28"></label>
 <span id="n"></span>
</div>
<div class="wrap">{table(df[COLS], '', 'main')}</div>
<p class="sub">Sources: data/med4_aa_peptide_gene_table.csv, data/hot1a3_aa_peptide_gene_table.csv; query envelopes in data/*_query_envelopes.csv.</p>
<script>
const T=document.getElementById('main'), rows=[...T.tBodies[0].rows], H=[...T.tHead.rows[0].cells].map(c=>c.textContent);
const ix=n=>H.indexOf(n);
function apply(){{
 const o=fo.value,r=fr.value,c=fc.value,w=fw.checked,t=ft.value.toLowerCase(); let n=0;
 for(const tr of rows){{const v=i=>tr.cells[i].textContent;
  const ok=(!o||v(ix('organism'))===o)&&(!r||v(ix('role'))===r)&&(!c||v(ix('aa_class')).split(' | ').includes(c))
   &&(!w||v(ix('weak_evidence_only'))==='no')&&(!t||tr.textContent.toLowerCase().includes(t));
  tr.style.display=ok?'':'none'; n+=ok;}}
 document.getElementById('n').textContent=n+' of '+rows.length+' rows shown';}}
['fo','fr','fc','fw','ft'].forEach(id=>document.getElementById(id).addEventListener('input',apply));
document.querySelectorAll('table').forEach(tb=>{{[...tb.tHead.rows[0].cells].forEach((th,i)=>th.addEventListener('click',()=>{{
 const b=tb.tBodies[0], rs=[...b.rows], asc=th.dataset.asc!=='1'; th.dataset.asc=asc?'1':'0';
 rs.sort((a,c)=>{{const x=a.cells[i].textContent,y=c.cells[i].textContent,nx=parseFloat(x),ny=parseFloat(y);
  const k=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y); return asc?k:-k}}); rs.forEach(r=>b.appendChild(r));}}))}});
apply();
</script></body></html>"""
out = REP / "med4_aa_peptide_gene_table.html"
out.write_text(page, encoding="utf-8")
print(out, len(page))
