"""Build analysis/reports/summary.html from analysis/data and figures (self-contained)."""
import base64
import html
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
DATA, FIG, REP = HERE / "data", HERE / "figures", HERE / "reports"
REP.mkdir(exist_ok=True)

CSS = """
:root{--up:#eb6834;--down:#2a78d6;--mid:#f0efec;--ink:#1f1f1e;--muted:#6b6a66;--line:#e4e3df}
body{font-family:system-ui,Segoe UI,sans-serif;color:var(--ink);max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.45}
h1{font-size:1.5rem}h2{font-size:1.15rem;margin-top:2rem}
table{border-collapse:collapse;font-size:.85rem;margin:.5rem 0}
th,td{border-bottom:1px solid var(--line);padding:.3rem .6rem;text-align:left}
th{cursor:pointer;background:#fafaf8;position:sticky;top:0}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.pos{color:var(--ink);border-left:3px solid var(--up)}.neg{color:var(--ink);border-left:3px solid var(--down)}
img{max-width:100%;border:1px solid var(--line)}
.cap{color:var(--muted);font-size:.85rem}
input{margin:.5rem 0;padding:.3rem;width:18rem}
@media print{input{display:none}table,img,tr{page-break-inside:avoid}th{position:static}}
"""
JS = """
document.querySelectorAll('table.sortable th').forEach((th,i)=>th.addEventListener('click',()=>{
 const tb=th.closest('table').tBodies[0];const rows=[...tb.rows];const asc=th.dataset.asc!=='1';th.dataset.asc=asc?'1':'0';
 rows.sort((a,b)=>{const x=a.cells[i].innerText,y=b.cells[i].innerText;const nx=parseFloat(x),ny=parseFloat(y);
  const c=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y);return asc?c:-c});rows.forEach(r=>tb.appendChild(r));}));
const f=document.getElementById('filter');if(f)f.addEventListener('input',()=>{const q=f.value.toLowerCase();
 document.querySelectorAll('#genes tbody tr').forEach(r=>r.style.display=r.innerText.toLowerCase().includes(q)?'':'none')});
"""


def table(df, tid=None, fc_col=None):
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    body = []
    for _, r in df.iterrows():
        cells = []
        for c in df.columns:
            v = r[c]
            if pd.isna(v):
                s = ""
            elif isinstance(v, float):
                s = f"{v:.4g}"
            else:
                s = str(v)
            cls = "num" if isinstance(v, (int, float)) and not isinstance(v, bool) else ""
            if c == fc_col and not pd.isna(v):
                cls += " pos" if v > 0 else " neg"
            cells.append(f'<td class="{cls.strip()}">{html.escape(s)}</td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    idattr = f' id="{tid}"' if tid else ""
    return f'<table class="sortable"{idattr}><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def img(stem):
    b = base64.b64encode((FIG / f"{stem}.png").read_bytes()).decode()
    return f'<img alt="{stem}" src="data:image/png;base64,{b}">'


rd = pd.read_csv(DATA / "readings.csv", encoding="utf-8")
ct = pd.read_csv(DATA / "controls.csv", encoding="utf-8").dropna(axis=1, how="all")
gate = pd.read_csv(DATA / "qc_identity_gate.csv", encoding="utf-8")
nt = pd.read_csv(DATA / "ntca_rows.csv", encoding="utf-8")
gt = pd.read_csv(DATA / "gene_table.csv", encoding="utf-8")

cap = ("Grey violin: log2FC of all genes in that experiment/time point. Open circles: the 11 ure/urt "
       "genes. Filled point: ntcA, coloured by sign (orange &gt; 0, blue &lt; 0), labelled with log2FC "
       "and the paper's significance call. Dashed lines: ±75th percentile of |log2FC| in that column. "
       "Urea and cyanate/nitrite are vs ammonium; N-dep is −N vs +NH4 at the stated time point.")

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>ntcA on urea — analysis summary</title>
<meta name="description" content="Decision rules applied to ntcA (PMM0246, PMT1831): readings, controls, identity gate, gene table, per-strain figures.">
<style>{CSS}</style></head><body>
<h1>ntcA on urea — analysis milestone</h1>
<p>What this milestone asked: Apply the pre-registered rules in proposal.md to ntcA on urea vs ammonium (MED4, MIT9313), with N deprivation as a detectability control and cyanate / nitrite as descriptive context.</p>
<h2>Readings (data/readings.csv)</h2>{table(rd.drop(columns=["experiment_id"]), fc_col="ntca_log2fc")}
<p>Only one urea reading is interpretable: MIT9313, suggestive up (not significant). MED4 is uninterpretable because its urea-gene control failed. No agreement between the strains can be claimed.</p>
<p class="cap">Cyanate (MED4) and nitrite (MIT9313) rows are descriptive and not gated by any control (gating = descriptive_ungated).</p>
<h2>ntcA rows used (data/ntca_rows.csv)</h2>{table(nt.drop(columns=["experiment_id"]), fc_col="log2fc")}
<h2>Controls (data/controls.csv)</h2>{table(ct)}
<p>MIT9313 urea-gene control: passes on the urea transporter genes (urtA, urtC, urtD significant up); the urease genes ureA–G are all below +0.39.</p>
<h2>Identity gate: MED4 urea vs MED4 cyanate (data/qc_identity_gate.csv)</h2>
{table(gate.drop(columns=["experiment_a", "experiment_b"]))}
<h2>Figures</h2>
<h3>MED4</h3>{img("ntca_med4")}<p class="cap">{cap} n = 1,696 genes per column.</p>
<h3>MIT9313</h3>{img("ntca_mit9313")}<p class="cap">{cap} n = 2,241 genes per column.</p>
<h2>Gene table (data/gene_table.csv)</h2>
<input id="filter" placeholder="filter (locus tag, gene, experiment…)">
{table(gt[["set", "experiment_key", "timepoint", "locus_tag", "gene_name", "log2fc", "padj", "expression_status", "abs_rank_pct"]], tid="genes", fc_col="log2fc")}
<h2>Files</h2><ul>
<li><a href="../scripts/01_run_rules.py">scripts/01_run_rules.py</a>, <a href="../scripts/02_figures.py">scripts/02_figures.py</a>, <a href="../scripts/build_reports.py">scripts/build_reports.py</a></li>
<li>data: <a href="../data/readings.csv">readings.csv</a>, <a href="../data/controls.csv">controls.csv</a>, <a href="../data/ntca_rows.csv">ntca_rows.csv</a>, <a href="../data/gene_table.csv">gene_table.csv</a>, <a href="../data/qc_identity_gate.csv">qc_identity_gate.csv</a>, <a href="../data/genome_log2fc_used.csv">genome_log2fc_used.csv</a></li>
<li>figures: <a href="../figures/ntca_med4.svg">ntca_med4.svg</a>, <a href="../figures/ntca_mit9313.svg">ntca_mit9313.svg</a></li>
</ul><script>{JS}</script></body></html>"""
(REP / "summary.html").write_text(page, encoding="utf-8")
print("wrote", REP / "summary.html", len(page), "bytes")
