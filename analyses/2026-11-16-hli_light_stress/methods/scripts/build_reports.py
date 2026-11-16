"""Build methods/reports/summary.html and methods/reports/controls.html from methods/data/.

Self-contained pages (data inlined as JSON, plain HTML/SVG/JS, no network).
Pages are rebuilt from the data, never edited by hand.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/methods/scripts/build_reports.py
"""
import html
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

METHODS = Path(__file__).resolve().parents[1]
DATA, REP = METHODS / "data", METHODS / "reports"
REP.mkdir(exist_ok=True)

CSS = """
:root{--bg:#fcfcfb;--ink:#1f1f1d;--muted:#6b6b66;--rule:#d9d8d4;--up:#eb6834;--down:#2a78d6;--mid:#f0efec;--na:#e4e3df;--card:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1a1a19;--ink:#ecebe8;--muted:#a3a29d;--rule:#3a3a37;--up:#d95926;--down:#3987e5;--mid:#383835;--na:#2c2c2a;--card:#222220}}
:root[data-theme="dark"]{--bg:#1a1a19;--ink:#ecebe8;--muted:#a3a29d;--rule:#3a3a37;--up:#d95926;--down:#3987e5;--mid:#383835;--na:#2c2c2a;--card:#222220}
body{background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;padding:24px 16px;max-width:1400px;margin:auto}
h1{font-size:22px;margin:0 0 4px} h2{font-size:17px;margin:28px 0 8px;border-bottom:1px solid var(--rule);padding-bottom:4px}
p.lead{color:var(--muted);margin-top:0} a{color:var(--down)}
table{border-collapse:collapse;font-size:12px;width:100%;background:var(--card)} th,td{border-bottom:1px solid var(--rule);padding:3px 6px;text-align:left;vertical-align:top}
th{cursor:pointer;position:sticky;top:0;background:var(--card)} td.num{text-align:right;font-variant-numeric:tabular-nums}
.wrap{overflow-x:auto;max-height:520px;overflow-y:auto;border:1px solid var(--rule)}
.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:8px 0}
.controls select,.controls input,.controls button{font:inherit;padding:2px 6px}
#tip{position:fixed;pointer-events:none;background:var(--card);border:1px solid var(--rule);padding:6px 8px;font-size:12px;display:none;max-width:360px;box-shadow:0 2px 8px rgba(0,0,0,.15);z-index:10}
.note{color:var(--muted);font-size:12px} figure{margin:8px 0} img{max-width:100%}
@media print{.controls{display:none}.wrap{max-height:none;overflow:visible}tr,figure{page-break-inside:avoid}body{background:#fff;color:#000}}
"""

SORT_JS = """
function sortable(tbl){tbl.querySelectorAll('th').forEach((th,i)=>{th.addEventListener('click',()=>{
 const b=tbl.tBodies[0];const rows=[...b.rows];const asc=th.dataset.asc!=='1';th.dataset.asc=asc?'1':'0';
 rows.sort((x,y)=>{let a=x.cells[i].dataset.v??x.cells[i].textContent,c=y.cells[i].dataset.v??y.cells[i].textContent;
  const na=parseFloat(a),nc=parseFloat(c);if(!isNaN(na)&&!isNaN(nc))return asc?na-nc:nc-na;return asc?a.localeCompare(c):c.localeCompare(a)});
 rows.forEach(r=>b.appendChild(r))})})}
document.querySelectorAll('table.sortable').forEach(sortable);
"""


def fmt(v):
    if isinstance(v, (float, np.floating)):
        if np.isnan(v):
            return ""
        if v != 0 and (abs(v) < 1e-3 or abs(v) >= 1e5):
            return f"{v:.2e}"
        return f"{v:.4g}"
    if isinstance(v, (bool, np.bool_)):
        return "yes" if v else "no"
    return "" if v is None else str(v)


def table(df: pd.DataFrame, tid: str = "") -> str:
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    body = []
    for r in df.itertuples(index=False):
        cells = []
        for v in r:
            num = isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, (bool, np.bool_))
            dv = f' data-v="{v}"' if num and not (isinstance(v, float) and np.isnan(v)) else ""
            cells.append(f'<td{dv}{" class=num" if num else ""}>{html.escape(fmt(v))}</td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<div class="wrap"><table class="sortable" id="{tid}"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def page(title, desc, body, extra_js=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<style>{CSS}</style></head><body>{body}<div id="tip"></div>
<script>{SORT_JS}{extra_js}</script></body></html>"""


def codefine_text() -> str:
    nb = (METHODS / "notebook.md").read_text(encoding="utf-8")
    m = re.search(r"## Co-define.*?\n\n(.*?)(\n## |\Z)", nb, re.S)
    txt = m.group(1).strip() if m else ""
    items = [re.sub(r"^\d+\.\s*", "", b.strip()) for b in re.split(r"\n(?=\d+\.)", txt) if b.strip()]
    out = []
    for it in items:
        lines = it.split("\n")
        main = html.escape(lines[0])
        subs = [html.escape(l.strip().lstrip("- ")) for l in lines[1:] if l.strip().startswith("-")]
        tail = [html.escape(l.strip()) for l in lines[1:] if l.strip() and not l.strip().startswith("-")]
        sub = ("<ul>" + "".join(f"<li>{s}</li>" for s in subs) + "</ul>") if subs else ""
        out.append(f"<li>{main}{sub}{(' ' + ' '.join(tail)) if tail else ''}</li>")
    return "<ol>" + "".join(out) + "</ol>"


SET_ROWS = [
    ("ribosomal_proteins", "Ribosomal proteins (K.2)", "Broad stress"),
    ("protein_folding", "Protein folding (L.3)", "Broad stress"),
    ("protein_degradation", "Protein degradation (L.4)", "Broad stress"),
    ("adaptation_N", "Adaptation: N (D.1.3)", "Specific"),
    ("adaptation_P", "Adaptation: P (D.1.5)", "Specific"),
    ("adaptation_Fe", "Adaptation: Fe (D.1.1)", "Specific"),
    ("adaptation_light_minus_hli", "Adaptation: light minus hli (D.1.2)", "Light"),
    ("photosystem_I", "Photosystem I (J.7)", "Photosynthesis"),
    ("co2_fixation", "CO2 fixation (J.2)", "Photosynthesis"),
    ("photosystem_II", "Photosystem II (J.8)", "Photosynthesis"),
    ("chaperones", "Chaperones (D.4)", "Failed references"),
    ("oxidative_stress", "Oxidative stress (D.1.4)", "Failed references"),
]
SET_ORDER = [a for a, _, _ in SET_ROWS]


def main():
    t = pd.read_csv(DATA / "control_tests.csv", encoding="utf-8")
    t["flags"] = t["flags"].fillna("")
    agg = pd.read_csv(DATA / "control_experiment_calls.csv", encoding="utf-8")
    fp = pd.read_csv(DATA / "random_fp_rates.csv", encoding="utf-8")
    fl = pd.read_csv(DATA / "flag_check_vs_proposal.csv", encoding="utf-8")
    flall = pd.read_csv(DATA / "flag_counts.csv", encoding="utf-8")
    sign = pd.read_csv(DATA / "psii_sign_check.csv", encoding="utf-8")
    spot = pd.read_csv(DATA / "spot_check_pathway_enrichment.csv", encoding="utf-8")
    ex = pd.read_csv(DATA / "experiments.csv", encoding="utf-8")
    gs = pd.read_csv(DATA / "gene_sets.csv", encoding="utf-8")
    ov = pd.read_csv(DATA / "gene_set_overlaps.csv", encoding="utf-8")
    rb = pd.read_csv(DATA / "reference_behaviour.csv", encoding="utf-8")
    global ROLE
    ROLE = gs.drop_duplicates("set").set_index("set")["role"].to_dict()

    n_tests = t[["experiment_id", "timepoint", "direction"]].drop_duplicates().shape[0]
    one = t[t.set == "photosystem_II"]
    sig = t[t.padj_bh < 0.05]
    facts = pd.DataFrame([
        ("Experiments (MED4, transcript)", len(ex)),
        ("Experiment × timepoint × direction tests", n_tests),
        ("Testable tests (not too few / not testable / descriptive)", int(one.testable.sum())),
        ("Tests flagged too few (<10 significant genes)", int(one["flags"].str.contains("too_few").sum())),
        ("Tests flagged genome-wide response (>30%)", int(one["flags"].str.contains("genome_wide").sum())),
        ("Tests not testable (down, up-only table)", int(one["flags"].str.contains("not_testable").sum())),
        ("Tests descriptive (no test)", int(one["flags"].str.contains("descriptive").sum())),
        ("Too-few flags differing from proposal Known limits", int(fl.mismatch.sum())),
        *[(f"Reference tests with BH padj < 0.05 (up / down, oriented): {s} [{ROLE[s]}]",
           f"{int(((sig.set == s) & (sig.direction_oriented == 'up')).sum())} / "
           f"{int(((sig.set == s) & (sig.direction_oriented == 'down')).sum())}") for s in SET_ORDER],
        ("Random-set tests with raw p < 0.05, testable tests",
         f"{fp[(fp.scope == 'testable_tests') & (fp.group == 'ALL')].frac_p_lt_05.iloc[0]:.3f}"),
        ("Spot check vs pathway_enrichment: max |Δp|", f"{spot.abs_diff.max():.1e}"),
        ("Gene-set sizes: " + ", ".join(["hli"] + SET_ORDER),
         ", ".join(str(int((gs.set == s).sum())) for s in ["hli"] + SET_ORDER)),
    ], columns=["Item", "Value"])

    files = sorted([f"../data/{p.name}" for p in DATA.glob("*.csv")] +
                   [f"../scripts/{p.name}" for p in (METHODS / "scripts").glob("*.py")] +
                   [f"../figures/{p.name}" for p in (METHODS / "figures").glob("*.png")] +
                   ["../hli_scoring.py", "../pipeline.py", "../kg_io.py", "../tests/test_hli_scoring.py"])
    summary = f"""
<h1>Methods milestone — summary</h1>
<p class="lead">hli genes: light response or broad stress response? Methods: gene and experiment lists, scoring module,
checks on reference gene sets. No hli result is computed or shown in this milestone.</p>
<h2>What this milestone asked</h2>{codefine_text()}
<h2>Run facts (counts from methods/data)</h2>{table(facts)}
<p class="note">Counts only; what they mean is written in the milestone notebook.</p>
<h2>Pages</h2><ul><li><a href="controls.html">Reference-set and random-set checks</a> — heatmap of every test, reference behaviour by group and stress type, gene-set sizes and overlaps,
flags vs the proposal, photosystem II direction check, spot check against pathway_enrichment, random-set rates, experiment list.</li></ul>
<h2>Files</h2><ul>{''.join(f'<li><a href="{f}">{html.escape(f)}</a></li>' for f in files)}</ul>"""
    (REP / "summary.html").write_text(page("Methods summary",
                                           "Methods milestone: gene/experiment lists, scoring module, reference-set checks (no hli results).",
                                           summary), encoding="utf-8")

    # ---------------- controls page
    cols = (t[["experiment_id", "label", "group", "timepoint", "timepoint_order", "orientation",
               "light_treatment_umol", "light_control_umol"]].drop_duplicates(["experiment_id", "timepoint"]))
    cells = t[["experiment_id", "timepoint", "set", "direction", "direction_oriented", "n_sig_in_set",
               "n_measured_in_background", "n_sig_total", "background_size", "background_type", "pvalue", "padj_bh",
               "flags", "pvalue_in_table"]].copy()
    hm = dict(cols=json.loads(cols.to_json(orient="records")), cells=json.loads(cells.to_json(orient="records")), sets=[list(x) for x in SET_ROWS])
    hm_js = "const HM=" + json.dumps(hm) + ";" + """
const GROUPS=['light_onset_photoperiod','electron_transport_DCMU','phage_dark','nonlight_stress','nonstress_possible_relief'];
const GL={light_onset_photoperiod:'Light onset / photoperiod',electron_transport_DCMU:'DCMU',phage_dark:'Phage dark',nonlight_stress:'Non-light stress',nonstress_possible_relief:'Non-stress'};
const SETS=HM.sets;
const idx={};HM.cells.forEach(c=>{idx[[c.experiment_id,c.timepoint,c.set,c.direction_oriented].join('|')]=c});
function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()}
function mix(a,b,t){const p=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));const A=p(a),B=p(b);return 'rgb('+A.map((x,i)=>Math.round(x+(B[i]-x)*t)).join(',')+')'}
function draw(){
 const order=document.getElementById('order').value;
 let cols=[...HM.cols];
 if(order==='group')cols.sort((a,b)=>GROUPS.indexOf(a.group)-GROUPS.indexOf(b.group)||a.label.localeCompare(b.label)||a.timepoint_order-b.timepoint_order);
 else cols.sort((a,b)=>a.light_treatment_umol-b.light_treatment_umol||a.light_control_umol-b.light_control_umol||GROUPS.indexOf(a.group)-GROUPS.indexOf(b.group)||a.label.localeCompare(b.label)||a.timepoint_order-b.timepoint_order);
 const cw=16,ch=20,left=420,top=80,rows=[];SETS.forEach(s=>['up','down'].forEach(d=>rows.push([s,d])));
 const W=left+cols.length*cw+10,H=top+rows.length*ch+10;
 const lim=6; // colour saturates at padj 1e-6
 const up=css('--up'),dn=css('--down'),mid=css('--mid'),na=css('--na'),ink=css('--ink'),mut=css('--muted');
 let s=`<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" font-size="10" font-family="system-ui">`;
 s+=`<defs><pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="4" stroke="${mut}" stroke-width="1"/></pattern></defs>`;
 rows.forEach((r,i)=>{if(i===0||rows[i-1][0][2]!==r[0][2])s+=`<text x="6" y="${top+i*ch+12}" fill="${ink}" font-weight="bold">${r[0][2]}</text>`;s+=`<text x="${left-6}" y="${top+i*ch+ch/2+3}" text-anchor="end" fill="${ink}">${r[0][1]} — ${r[1]}</text>`});
 const blk=(a,b,v)=>{const t=order==='group'?GL[v]:v+' µmol',x=left+(a+b)/2*cw;return (b-a)<5&&order==='group'?`<text transform="translate(${x+3},${top-6}) rotate(-90)" fill="${ink}" font-size="9">${t}</text>`:`<text x="${x}" y="${top-8}" text-anchor="middle" fill="${ink}" font-size="9">${t}</text>`};let prev=null,start=0;const key=c=>order==='group'?c.group:String(c.light_treatment_umol);
 cols.forEach((c,j)=>{const k=key(c);if(prev!==null&&k!==prev){s+=`<line x1="${left+j*cw}" x2="${left+j*cw}" y1="${top-4}" y2="${top+rows.length*ch}" stroke="${ink}"/>`;
   s+=blk(start,j,prev);start=j}prev=k});
 s+=blk(start,cols.length,prev);
 cols.forEach((c,j)=>rows.forEach((r,i)=>{const cell=idx[[c.experiment_id,c.timepoint,r[0][0],r[1]].join('|')];if(!cell)return;
   const x=left+j*cw,y=top+i*ch;let fill,mark='';
   if(cell.flags.match(/not_testable|descriptive/))fill=na;else if(cell.flags.match(/too_few/))fill='url(#hatch)';
   else{const v=-Math.log10(Math.max(cell.padj_bh,1e-300));fill=mix(mid,r[1]==='up'?up:dn,Math.min(1,v/lim));if(cell.padj_bh<0.05)mark=`<text x="${x+cw/2}" y="${y+ch/2+4}" text-anchor="middle" fill="${ink}">*</text>`}
   if(cell.flags.match(/genome_wide/))mark+=`<circle cx="${x+cw-4}" cy="${y+4}" r="1.8" fill="${ink}"/>`;
   s+=`<rect class="c" data-k="${[c.experiment_id,c.timepoint,r[0][0],r[1]].join('|')}" data-l="${c.label}" x="${x+1}" y="${y+1}" width="${cw-2}" height="${ch-2}" fill="${fill}" stroke="${css('--rule')}" stroke-width="0.3"/>${mark}`}));
 for(let k=1;k<rows.length;k++)if(rows[k][0][2]!==rows[k-1][0][2])s+=`<line x1="6" x2="${left+cols.length*cw}" y1="${top+k*ch}" y2="${top+k*ch}" stroke="${ink}" stroke-width="${rows[k][0][2]==='Failed references'?3:1}"/>`;
 s+='</svg>';document.getElementById('hm').innerHTML=s;
 const tip=document.getElementById('tip');
 document.querySelectorAll('#hm rect.c').forEach(el=>{el.addEventListener('mousemove',e=>{const c=idx[el.dataset.k];
   const f=v=>v==null?'—':(v<1e-3?v.toExponential(2):v.toPrecision(3));
   tip.innerHTML=`<b>${el.dataset.l}</b> · ${c.timepoint}<br>${c.set} · oriented ${c.direction_oriented} (raw ${c.direction})<br>`+
    `in set & significant: ${c.n_sig_in_set??'—'} of ${c.n_measured_in_background} measured<br>significant genome-wide: ${c.n_sig_total} of ${c.background_size} (${c.background_type})<br>`+
    `p = ${f(c.pvalue)} · BH padj = ${f(c.padj_bh)}${c.pvalue_in_table!=null?' · in-table p = '+f(c.pvalue_in_table):''}<br>flags: ${c.flags||'none'}`;
   tip.style.display='block';tip.style.left=Math.min(e.clientX+12,innerWidth-370)+'px';tip.style.top=(e.clientY+12)+'px'});
  el.addEventListener('mouseleave',()=>tip.style.display='none')})}
document.getElementById('order').addEventListener('change',draw);draw();
function filt(){const s=document.getElementById('fset').value,q=document.getElementById('fq').value.toLowerCase();
 document.querySelectorAll('#tests tbody tr').forEach(r=>{const t=r.textContent.toLowerCase();r.style.display=((!s||r.cells[6].textContent===s)&&(!q||t.includes(q)))?'':'none'})}
document.getElementById('fset').addEventListener('change',filt);
document.getElementById('rbscope').addEventListener('change',e=>{const v=e.target.value;document.querySelectorAll('#rb tbody tr').forEach(r=>{r.style.display=(!v||r.cells[2].textContent===v)?'':'none'})});document.getElementById('fq').addEventListener('input',filt);
"""
    test_cols = ["label", "group", "timepoint", "direction", "orientation", "direction_oriented", "set", "set_role", "test_type",
                 "background_type", "background_size", "n_measured_in_background", "n_sig_in_set", "n_sig_total",
                 "genome_share_sig", "set_share_sig", "pvalue", "padj_bh", "flags", "pvalue_in_table",
                 "padj_in_table_bh", "experiment_id"]
    agg_cols = ["label", "group", "set", "set_role", "direction", "direction_oriented", "timepoint_count", "p_exp_bonferroni",
                "padj_exp_bh", "experiment_call_oriented", "experiment_id"]
    ex_cols = ["label", "group", "study", "stress_type", "omics", "table_scope", "test_type", "test_type_note",
               "up_only", "orientation", "in_table_group", "control_timing", "light_treatment_umol",
               "light_control_umol", "light_intensity_raw", "treatment_text", "control_text", "timepoints",
               "experiment_id"]
    fl_cols = ["label", "timepoint", "direction", "n_sig_total", "background_size", "genome_share_sig", "flags",
               "too_few_in_proposal", "mismatch"]
    body = f"""
<h1>Reference-set and random-set checks</h1>
<p class="lead">Ten Cyanorak reference sets (broad stress, nitrogen / phosphorus / iron / light adaptation, photosynthesis),
the two failed references from the first iteration (chaperones D.4, oxidative stress D.1.4), and size-matched random sets,
tested in every MED4 experiment × timepoint × direction. No hli results.</p>
<h2>Heatmap</h2>
<div class="controls"><label>Column order <select id="order"><option value="group">by experiment group</option>
<option value="light">by treatment-arm light level</option></select></label></div>
<div class="wrap" style="max-height:none" id="hm"></div>
<p class="note">Cell colour = −log10(BH padj) (saturates at 6), orange for up rows, blue for down rows (BH per gene set across all testable tests).
Direction is oriented: for extended darkness and both constant-dark experiments up/down are swapped so up = higher with more light.
Hatched = fewer than 10 genes significant in that direction. Gray = not testable (down, up-only table) or descriptive.
Dot = more than 30% of measured genes significant. * = padj &lt; 0.05. Hover a cell for counts and p-values.
Static versions: <a href="../figures/controls_heatmap_by_group.png">by group</a>, <a href="../figures/controls_heatmap_by_light.png">by light level</a>.</p>
<h2>Reference behaviour</h2>
<p class="note">Per set × scope: testable tests and tests with BH padj &lt; 0.05 by oriented direction. Scopes: experiment group;
stress type inside the non-light stress group; for the N / P / Fe adaptation sets, the set's own stress vs other non-light stresses vs all other tests;
for ribosomal proteins, the non-light stress tests (frac_sig_down). Counts only.</p>
<div class="controls"><label>Scope type <select id="rbscope"><option value="">all</option>{"".join(f"<option>{x}</option>" for x in rb.scope_type.unique())}</select></label></div>
{table(rb, "rb")}
<h2>Gene sets: sizes and overlaps</h2>
<p class="note">Overlapping genes are kept in both sets (reported, not removed). Only pairs with at least one shared gene are listed.</p>
{table(gs[~gs.set.str.startswith("hli_group")].groupby(["set", "role"]).size().reset_index(name="n_genes"))}
{table(ov[ov.n_overlap > 0])}
<h2>All tests</h2>
<div class="controls"><label>Set <select id="fset"><option value="">all</option>{"".join(f"<option>{x}</option>" for x in SET_ORDER)}</select></label>
<label>Search <input id="fq" placeholder="label, flag, timepoint"></label></div>
{table(t[test_cols], "tests")}
<h2>Per-experiment aggregate</h2>
<p class="note">p_exp = smallest testable-timepoint p × number of testable timepoints (cap 1); BH across experiment × direction rows, per set. Call uses oriented direction.</p>
{table(agg[agg_cols])}
<h2>Flags vs proposal Known limits</h2>
<p class="note">Tests flagged too few, genome-wide, not testable or descriptive, or listed as too few in the proposal. mismatch = computed too-few flag differs from the proposal list.</p>
{table(fl[fl_cols])}
<p class="note">Totals per group:</p>
{table(flall.groupby("group")[["too_few", "genome_wide_response", "not_testable", "descriptive", "approximate", "testable"]].sum().reset_index())}
<h2>Photosystem II direction check</h2>
<p class="note">PSII genes (31) by call per timepoint, raw (unoriented) direction. High white light: a significant-only table (genes not in the table are counted separately).</p>
{table(sign.drop(columns=["experiment_id"]))}
<h2>Spot check against pathway_enrichment</h2>
<p class="note">N deprivation microarray (Tolonen 2006, full table). pathway_enrichment: cyanorak_role, term_ids J.8 and D.4, background table_scope. Empty rows: pathway_enrichment skips gene sets with no significant genes.</p>
{table(spot.drop(columns=["experiment_id"]))}
<h2>Random sets</h2>
<p class="note">200 random sets per timepoint, size = number of target-set genes inside that timepoint's main background, drawn from that background (seed 20261116). Share of random-set tests with raw p &lt; 0.05.</p>
{table(fp)}
<h2>Experiments</h2>{table(ex[ex_cols])}
"""
    (REP / "controls.html").write_text(page("Reference-set checks",
                                            "Reference and random gene sets across all 29 MED4 experiments: heatmap, reference behaviour, flags vs proposal, PSII sign check, pathway_enrichment spot check.",
                                            body, hm_js), encoding="utf-8")
    print("wrote", [p.name for p in REP.glob("*.html")])


if __name__ == "__main__":
    main()
