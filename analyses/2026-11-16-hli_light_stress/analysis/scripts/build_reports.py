"""Build analysis/reports/*.html from analysis/data/ (self-contained, offline, interactive hover).

Pages: summary.html, hli_heatmaps.html, aggregate.html, light_readings.html.
Facts and counts only; interpretation lives in analysis/notebook.md (main thread).

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/build_reports.py
"""
import html
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS.parent / "methods"))
import kg_io  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

DATA, REP, FIG = ANALYSIS / "data", ANALYSIS / "reports", ANALYSIS / "figures"
REP.mkdir(exist_ok=True)
SET_ROWS = [("hli", "hli (23 genes, 14 CK groups)", "Target")] + kg_io.set_rows()
BLOCK_ORDER = ["light_onset", "constant_dark_vs_light", "schedule_extension", "electron_transport_DCMU",
               "phage_dark", "nonlight_stress", "nonstress_possible_relief"]
BLOCK_LABEL = {"light_onset": "Light onset", "constant_dark_vs_light": "Constant dark vs light",
               "schedule_extension": "Schedule extension", "electron_transport_DCMU": "DCMU",
               "phage_dark": "Phage dark", "nonlight_stress": "Non-light stress",
               "nonstress_possible_relief": "Non-stress"}
SCOPES = [("light_reading_group", "light_onset", "Light onset"),
          ("light_reading_group", "constant_dark_vs_light", "Const. dark vs light"),
          ("light_reading_group", "schedule_extension", "Schedule ext."),
          ("light_reading_group", "phage_dark", "Phage, dark"),
          ("nonlight_stress_type", "carbon", "CO2"), ("nonlight_stress_type", "iron", "Iron"),
          ("nonlight_stress_type", "nitrogen", "Nitrogen"), ("nonlight_stress_type", "phosphorus", "Phosphorus"),
          ("nonlight_stress_type", "salt", "Salt"), ("nonlight_stress_type", "viral", "Phage, light"),
          ("group", "nonstress_possible_relief", "Non-stress")]
DIRECTION_NOTE = "Direction is treatment vs control, as stored in the KG (no light flip)."

CSS = """
:root{color-scheme:light;--bg:#ffffff;--ink:#1f1f1d;--muted:#6b6b66;--rule:#d9d8d4;--up:#eb6834;--down:#2a78d6;--mid:#f0efec;--ns:#d9d8d4;--na:#e4e3df;--card:#ffffff}
.legend-d{font-size:12px;margin:6px 0;line-height:1.9}
body{background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;margin:0 auto;padding:24px 16px;max-width:1400px}
h1{font-size:22px;margin:0 0 4px} h2{font-size:17px;margin:28px 0 8px;border-bottom:1px solid var(--rule);padding-bottom:4px}
p.lead{color:var(--muted);margin-top:0} a{color:var(--down)}
table{border-collapse:collapse;font-size:12px;width:100%;background:var(--card)} th,td{border-bottom:1px solid var(--rule);padding:3px 6px;text-align:left;vertical-align:top}
th{cursor:pointer;position:sticky;top:0;background:var(--card)} td.num{text-align:right;font-variant-numeric:tabular-nums}
.wrap{overflow-x:auto;max-height:520px;overflow-y:auto;border:1px solid var(--rule)}
.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:8px 0}
.controls select,.controls input{font:inherit;padding:2px 6px}
#tip{position:fixed;pointer-events:none;background:var(--card);border:1px solid var(--rule);padding:6px 8px;font-size:12px;display:none;max-width:380px;box-shadow:0 2px 8px rgba(0,0,0,.15);z-index:10}
.note{color:var(--muted);font-size:12px} img{max-width:100%}
.legend span{display:inline-block;width:12px;height:12px;vertical-align:middle;margin:0 4px 0 12px;border:1px solid var(--rule)}
@media print{.controls{display:none}.wrap{max-height:none;overflow:visible}tr{page-break-inside:avoid}body{background:#fff;color:#000}}
"""

JS = r"""
function sortable(tbl){tbl.querySelectorAll('th').forEach((th,i)=>{th.addEventListener('click',()=>{
 const b=tbl.tBodies[0];const rows=[...b.rows];const asc=th.dataset.asc!=='1';th.dataset.asc=asc?'1':'0';
 rows.sort((x,y)=>{let a=x.cells[i].dataset.v??x.cells[i].textContent,c=y.cells[i].dataset.v??y.cells[i].textContent;
  const na=parseFloat(a),nc=parseFloat(c);if(!isNaN(na)&&!isNaN(nc))return asc?na-nc:nc-na;return asc?a.localeCompare(c):c.localeCompare(a)});
 rows.forEach(r=>b.appendChild(r))})})}
document.querySelectorAll('table.sortable').forEach(sortable);
function filterTable(inputId,tableId){const el=document.getElementById(inputId);if(!el)return;el.addEventListener('input',()=>{const q=el.value.toLowerCase();
 document.querySelectorAll('#'+tableId+' tbody tr').forEach(r=>{r.style.display=(!q||r.textContent.toLowerCase().includes(q))?'':'none'})})}
const esc=t=>String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()}
function mix(a,b,t){const p=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));const A=p(a),B=p(b);t=Math.max(0,Math.min(1,t));return 'rgb('+A.map((x,i)=>Math.round(x+(B[i]-x)*t)).join(',')+')'}
// spec: {el, rows:[{k,label,band}], cols:[{k,label,detail,block,light,rank,sub}], cells:{rk|ck:{...}}, cw, ch, left, colLabels}
function grid(spec, order){
 const ink=css('--ink'),mut=css('--muted'),up=css('--up'),dn=css('--down'),mid=css('--mid'),ns=css('--ns'),na=css('--na'),rule=css('--rule');
 let cols=[...spec.cols];
 if(order==='light')cols.sort((a,b)=>a.light-b.light||a.lightc-b.lightc||a.rank-b.rank||a.label.localeCompare(b.label)||a.sub-b.sub);
 else cols.sort((a,b)=>a.rank-b.rank||a.label.localeCompare(b.label)||a.sub-b.sub);
 const cw=spec.cw||16,ch=spec.ch||18,left=spec.left||300,top=spec.top||120,LB=spec.colLabels?spec.lb||400:10;
 const rows=spec.rows,W=left+cols.length*cw+10,H=top+rows.length*ch+LB;
 let s=`<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" font-size="10" font-family="system-ui">`;
 s+=`<defs><pattern id="h_${spec.el}" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="4" stroke="${mut}" stroke-width="1"/></pattern></defs>`;
 rows.forEach((r,i)=>{if(r.band!==undefined&&(i===0||rows[i-1].band!==r.band))s+=`<text x="4" y="${top+i*ch+12}" fill="${ink}" font-weight="bold">${esc(r.band)}</text>`;
   s+=`<text x="${left-6}" y="${top+i*ch+ch/2+3}" text-anchor="end" fill="${ink}">${esc(r.label)}</text>`;
   if(i>0&&r.band!==undefined&&rows[i-1].band!==r.band)s+=`<line x1="4" x2="${left+cols.length*cw}" y1="${top+i*ch}" y2="${top+i*ch}" stroke="${ink}" stroke-width="1.5"/>`});
 const key=c=>order==='light'?String(c.light):c.block;let start=0;
 const blk=(a,b,v)=>{const t=order==='light'?v+' µmol':(spec.blockLabel[v]||v),x=spec.left+(a+b)/2*cw;
   const by=spec.colLabels?top-8:top-44;return ((b-a)*cw<t.length*5.6)?`<text transform="translate(${x+3},${top-6}) rotate(-90)" fill="${ink}" font-size="9">${esc(t)}</text>`:`<text x="${x}" y="${by}" text-anchor="middle" fill="${ink}" font-size="9" font-weight="bold">${esc(t)}</text>`};
 for(let j=1;j<=cols.length;j++){if(j===cols.length||key(cols[j])!==key(cols[start])){s+=blk(start,j,key(cols[start]));
   if(j<cols.length)s+=`<line x1="${left+j*cw}" x2="${left+j*cw}" y1="${top-4}" y2="${top+rows.length*ch}" stroke="${ink}"/>`;start=j}}
 cols.forEach((c,j)=>rows.forEach((r,i)=>{const cell=spec.cells[r.k+'|'+c.k];if(!cell)return;const x=left+j*cw,y=top+i*ch,w=cw-2,h=ch-2;let body='';
   if(cell.t==='cat'){const f={up:up,down:dn,ns:ns,neither:ns}[cell.v];
     if(cell.v==='both')body=`<rect x="${x+1}" y="${y+1}" width="${w}" height="${h/2}" fill="${up}"/><rect x="${x+1}" y="${y+1+h/2}" width="${w}" height="${h/2}" fill="${dn}"/>`;
     else if(f)body=`<rect x="${x+1}" y="${y+1}" width="${w}" height="${h}" fill="${f}"/>`;
     else body=`<rect x="${x+1}" y="${y+1}" width="${w}" height="${h}" fill="url(#h_${spec.el})" stroke="${rule}" stroke-width="0.3"/>`}
   else if(cell.t==='val'){let f,m='';if(cell.na)f=na;else if(cell.few)f=`url(#h_${spec.el})`;
     else{f=mix(mid,r.dir==='up'?up:dn,Math.min(1,cell.v/6));if(cell.sig)m=`<text x="${x+cw/2}" y="${y+ch/2+4}" text-anchor="middle" fill="${ink}">*</text>`}
     if(cell.gw)m+=`<circle cx="${x+cw-4}" cy="${y+4}" r="1.6" fill="${ink}"/>`;body=`<rect x="${x+1}" y="${y+1}" width="${w}" height="${h}" fill="${f}" stroke="${rule}" stroke-width="0.3"/>${m}`}
   else if(cell.t==='net'){if(cell.nm)body=`<rect x="${x+1}" y="${y+1}" width="${w}" height="${h}" fill="url(#h_${spec.el})" stroke="${rule}" stroke-width="0.3"/>`;else body=`<rect x="${x+1}" y="${y+1}" width="${w}" height="${h}" fill="${mix(mid,cell.v>=0?up:dn,Math.abs(cell.v))}" stroke="${rule}" stroke-width="0.3"/>`}
   else if(cell.t==='split'){if(cell.n===0)body=`<rect x="${x+1}" y="${y+1}" width="${w}" height="${h}" fill="none" stroke="${rule}"/><text x="${x+cw/2}" y="${y+ch/2+3}" text-anchor="middle" fill="${mut}" font-size="8">no test</text>`;
     else body=`<rect x="${x+1}" y="${y+1}" width="${w/2}" height="${h}" fill="${mix(mid,up,cell.fu)}"/><rect x="${x+1+w/2}" y="${y+1}" width="${w/2}" height="${h}" fill="${mix(mid,dn,cell.fd)}"/>`+
      `<text x="${x+1+w/4}" y="${y+ch/2+2}" text-anchor="middle" fill="${ink}" font-size="11">${cell.nu}</text><text x="${x+1+3*w/4}" y="${y+ch/2+2}" text-anchor="middle" fill="${ink}" font-size="11">${cell.nd}</text>`+
      `<text x="${x+cw/2}" y="${y+ch-4}" text-anchor="middle" fill="${mut}" font-size="8">n=${cell.n}</text>`}
   s+=`<g class="c" data-k="${esc(r.k+'|'+c.k)}">${body}<rect x="${x}" y="${y}" width="${cw}" height="${ch}" fill="transparent"/></g>`}));
 if(spec.colLabels)cols.forEach((c,j)=>{s+=`<text transform="translate(${left+j*cw+cw/2+3},${top+rows.length*ch+6}) rotate(90)" fill="${ink}" font-size="8">${esc(c.detail)}</text>`});
 else cols.forEach((c,j)=>{s+=`<text x="${left+j*cw+cw/2}" y="${top-12}" text-anchor="middle" fill="${ink}" font-size="10">${esc(c.label)}</text>`});
 s+='</svg>';const host=document.getElementById(spec.el);host.innerHTML=s;const tip=document.getElementById('tip');
 host.querySelectorAll('g.c').forEach(g=>{g.addEventListener('mousemove',e=>{tip.innerHTML=spec.cells[g.dataset.k].tip;tip.style.display='block';
   tip.style.left=Math.min(e.clientX+12,innerWidth-390)+'px';tip.style.top=(e.clientY+12)+'px'});g.addEventListener('mouseleave',()=>tip.style.display='none')})}
function wireGrid(spec,selId){const sel=selId?document.getElementById(selId):null;const draw=()=>grid(spec,sel?sel.value:'group');if(sel)sel.addEventListener('change',draw);draw()}
"""


def read(name):
    """Read an analysis CSV; display overrides (A.3-A.6: labels and grouping only) applied in memory."""
    import display_overrides as dov
    return dov.apply(pd.read_csv(DATA / name, encoding="utf-8", keep_default_na=False, na_values=[""]))


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


def table(df, tid=""):
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


def page(title, desc, body, js=""):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>'
            f'<meta name="description" content="{html.escape(desc)}"><style>{CSS}</style></head><body>{body}'
            f'<div id="tip"></div><script>{JS}{js}</script></body></html>')


def p_(v):
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else (f"{v:.2e}" if v < 1e-3 else f"{v:.3g}")


def col_specs(t):
    c = (t[["experiment_id", "label", "label_detailed", "group", "light_reading_group", "timepoint", "timepoint_order",
            "light_treatment_umol", "light_control_umol"]].drop_duplicates(["experiment_id", "timepoint"]))
    out = []
    for r in c.itertuples():
        block = r.light_reading_group if r.light_reading_group != "none" else r.group
        out.append(dict(k=f"{r.experiment_id}|{r.timepoint}", label=r.label, detail=f"{r.label_detailed} · {r.timepoint}",
                        block=block, rank=BLOCK_ORDER.index(block), light=float(r.light_treatment_umol),
                        lightc=float(r.light_control_umol), sub=float(r.timepoint_order)))
    return out


def codefine():
    nb = (ANALYSIS / "notebook.md").read_text(encoding="utf-8")
    m = re.search(r"## Co-define.*?\n\n(.*?)(\n## |\Z)", nb, re.S)
    items = [html.escape(re.sub(r"^\s*-\s*", "", ln).replace("**", "")) for ln in (m.group(1) if m else "").split("\n")
             if ln.strip()]
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def main():
    t = read("hli_tests.csv")
    gc = read("hli_gene_calls.csv")
    calls = read("experiment_calls.csv")
    lr = read("light_readings.csv")
    res = read("resemblance.csv")
    rb = read("hli_random_baseline.csv")
    cov = read("qc_hli_coverage.csv")
    qcbh = read("qc_bh_recompute.csv")
    sign = read("qc_de_sign.csv")
    qcde = read("qc_de.csv")
    h = t[t.set == "hli"]
    import display_overrides as dov
    pc = t[t.experiment_id == dov.COCULT25].copy()
    pc["sig"] = pc.testable & (pc.padj_bh < 0.05)
    rows_ = []
    for (st, tp), g in pc.groupby(["set", "timepoint"], sort=False):
        gi = g.set_index("direction")
        u, d_ = gi.loc["up"], gi.loc["down"]
        call = ("both" if u.sig and d_.sig else "up" if u.sig else "down" if d_.sig else
                "not testable" if not (u.testable or d_.testable) else "neither")
        rows_.append(dict(set=st, timepoint=tp, label_detailed=u.label_detailed, display_group=u.group, call=call,
                          padj_up=u.padj_bh, flags_up=u.flags, padj_down=d_.padj_bh, flags_down=d_.flags))
    pt_calls = pd.DataFrame(rows_)
    cols = col_specs(t)

    # ---------------- hli_heatmaps.html
    genes = gc[["locus_tag", "ck_group", "gene_name"]].drop_duplicates("locus_tag").sort_values(["ck_group", "locus_tag"])
    g_rows = [dict(k=r.locus_tag, label=f"{r.locus_tag} ({r.ck_group.replace('cyanorak:', '')})") for r in genes.itertuples()]
    g_cells = {}
    for r in gc.itertuples():
        v = {"not_measured": "nm"}.get(r.call, r.call)
        g_cells[f"{r.locus_tag}|{r.experiment_id}|{r.timepoint}"] = dict(
            t="cat", v=v, tip=(f"<b>{html.escape(r.locus_tag)}</b> ({html.escape(r.ck_group)})<br>{html.escape(r.label_detailed)}"
                               f" · {html.escape(r.timepoint)}<br>call: <b>{r.call}</b> ({r.call_source})<br>"
                               f"log2FC {p_(r.log2fc)} · padj {p_(r.padj)}<br>test type: {r.test_type}"))
    gspec = dict(el="ghm", rows=g_rows, cols=cols, cells=g_cells, blockLabel=BLOCK_LABEL, colLabels=True, left=200, top=120)
    s_rows = [dict(k=f"{s}|{d}", label=f"{l} — {d}", band=b, dir=d) for s, l, b in SET_ROWS for d in ("up", "down")]
    s_cells = {}
    for r in t.itertuples():
        fl = r.flags if isinstance(r.flags, str) else ""
        tip = (f"<b>{html.escape(r.set)}</b> · {r.direction}<br>{html.escape(r.label_detailed)} · {html.escape(r.timepoint)}<br>"
               f"{fmt(r.n_sig_in_set)} of {r.n_measured_in_background} set genes significant; {r.n_sig_total} of "
               f"{r.background_size} genome-wide ({r.background_type})<br>both directions: {p_(r.share_sig_both_directions)}"
               f" of background<br>p {p_(r.pvalue)} · BH padj {p_(r.padj_bh)}"
               + (f" · in-table p {p_(r.pvalue_in_table)}" if not np.isnan(r.pvalue_in_table) else "")
               + (f"<br>random-set empirical p {p_(r.empirical_p_random)}" if r.set == "hli" and not np.isnan(r.empirical_p_random) else "")
               + (f"<br>CK groups measured {fmt(r.n_groups_measured)}, up {fmt(r.n_groups_up)}, down {r.n_groups_down_reported}"
                  if r.set == "hli" else "") + f"<br>flags: {fl or 'none'}")
        s_cells[f"{r.set}|{r.direction}|{r.experiment_id}|{r.timepoint}"] = dict(
            t="val", na=("not_testable" in fl or "descriptive" in fl), few=("too_few" in fl),
            v=(-np.log10(max(r.padj_bh, 1e-300)) if not np.isnan(r.padj_bh) else 0.0),
            sig=bool(r.padj_bh < 0.05) if not np.isnan(r.padj_bh) else False, gw="genome_wide" in fl, tip=tip)
    sspec = dict(el="shm", rows=s_rows, cols=cols, cells=s_cells, blockLabel=BLOCK_LABEL, colLabels=True, left=420, top=120)
    hcols = ["label", "label_detailed", "light_reading_group", "more_light_arm", "timepoint", "direction",
             "n_measured_in_background", "n_sig_in_set", "n_sig_total", "background_type", "share_sig_both_directions",
             "pvalue", "padj_bh", "flags", "pvalue_in_table", "padj_in_table_bh", "empirical_p_random",
             "n_groups_measured", "n_groups_up", "n_groups_down_reported", "experiment_id"]
    body = f"""<h1>hli heatmaps</h1>
<p class="lead">MED4: the 23 hli genes and the hli set-level tests next to every reference set, in 29 experiments. {DIRECTION_NOTE}</p>
<div class="controls"><label>Column order <select id="ord">
<option value="group">by light reading / experiment group</option><option value="light">by treatment-arm light level</option></select></label></div>
<h2>Gene level: 23 hli genes</h2>
<p class="legend note"><span style="background:var(--up)"></span>up <span style="background:var(--down)"></span>down
<span style="background:var(--ns)"></span>not significant <span style="background:repeating-linear-gradient(45deg,var(--muted) 0 1px,transparent 1px 4px)"></span>not measured.
Rows ordered by Cyanorak CK group. In significant-only tables, a gene absent from the table is not significant (genome background).
Hover for log2FC and padj.</p>
<div class="wrap" style="max-height:none" id="ghm"></div>
<h2>Set level: hli and the reference sets</h2>
<p class="note">Cell colour = −log10(BH padj), saturating at 6; orange up rows, blue down rows; * padj &lt; 0.05; hatched = fewer than 10
significant genes; gray = not testable or descriptive; dot = more than 30% of measured genes significant in that direction.</p>
<div class="wrap" style="max-height:none" id="shm"></div>
<p class="note">Static figures: <a href="../figures/hli_gene_heatmap_by_group.png">genes by group</a>, <a href="../figures/hli_gene_heatmap_by_light.png">genes by light</a>,
<a href="../figures/set_band_by_group.png">sets by group</a>, <a href="../figures/set_band_by_light.png">sets by light</a>.</p>
<h2>hli tests</h2><div class="controls"><input id="fh" placeholder="filter"></div>{table(h[hcols], "th")}
<h2>hli random baseline</h2><p class="note">Per hli test: fraction of the 200 size-matched random sets (same background) with p ≤ the hli p.</p>
{table(rb[["label", "timepoint", "direction", "hli_pvalue", "random_set_size", "n_random", "n_random_p_le_hli", "empirical_p_random", "random_frac_p_lt_05", "flags", "testable"]], "trb")}
<h2>hli gene calls</h2><div class="controls"><input id="fg" placeholder="filter (locus tag, label, call)"></div>
{table(gc[["locus_tag", "ck_group", "label", "label_detailed", "timepoint", "call", "call_source", "log2fc", "padj", "test_type", "experiment_id"]], "tg")}"""
    js = (f"const GS={json.dumps(gspec)};const SS={json.dumps(sspec)};"
          "const o=document.getElementById('ord');const d=()=>{grid(GS,o.value);grid(SS,o.value)};o.addEventListener('change',d);d();"
          "filterTable('fh','th');filterTable('fg','tg');")
    (REP / "hli_heatmaps.html").write_text(page("hli heatmaps", "Gene-level hli calls and set-level tests for hli and all reference sets in 29 MED4 experiments.", body, js), encoding="utf-8")

    # ---------------- aggregate.html
    a_rows = [dict(k=s, label=l, band=b) for s, l, b in SET_ROWS]
    a_cols = [dict(k=f"{st}|{sc}", label=lab, detail=lab, block=("light" if st == "light_reading_group" else st),
                   rank=i, light=i, lightc=0, sub=0) for i, (st, sc, lab) in enumerate(SCOPES)]
    ridx = res.set_index(["set", "scope_type", "scope"])
    a_cells = {}
    for s, l, b in SET_ROWS:
        for st, sc, lab in SCOPES:
            r = ridx.loc[(s, st, sc)]
            n = int(r.n_testable)
            a_cells[f"{s}|{st}|{sc}"] = dict(t="split", n=n, nu=int(r.n_sig_up), nd=int(r.n_sig_down),
                                            fu=0 if n == 0 else float(r.frac_sig_up), fd=0 if n == 0 else float(r.frac_sig_down),
                                            tip=f"<b>{html.escape(l)}</b><br>{html.escape(lab)}: {int(r.n_sig_up)} up, {int(r.n_sig_down)} down of {n} testable tests ({int(r.n_experiments)} experiments)")
    aspec = dict(el="agg", rows=a_rows, cols=a_cols, cells=a_cells, colLabels=False, cw=92, ch=34, left=330, top=80,
                 blockLabel={"light": "Light readings", "nonlight_stress_type": "Non-light stress by type", "group": "Non-stress"})
    ecols = [dict(k=r.experiment_id, label=r.label, detail=r.label_detailed,
                  block=(r.light_reading_group if r.light_reading_group != "none" else r.group),
                  rank=BLOCK_ORDER.index(r.light_reading_group if r.light_reading_group != "none" else r.group),
                  light=float(t[t.experiment_id == r.experiment_id].light_treatment_umol.iloc[0]),
                  lightc=float(t[t.experiment_id == r.experiment_id].light_control_umol.iloc[0]), sub=0)
             for r in calls.drop_duplicates("experiment_id").itertuples()]
    e_cells = {}
    for (eid, s), g in calls.groupby(["experiment_id", "set"]):
        call = g.experiment_call.iloc[0]
        gi = g.set_index("direction")
        tip = (f"<b>{html.escape(s)}</b><br>{html.escape(g.label_detailed.iloc[0])}<br>call: <b>{call}</b><br>"
               + "<br>".join(f"{d}: {gi.at[d, 'timepoint_count']}, p_exp {p_(gi.at[d, 'p_exp_bonferroni'])}, "
                             f"BH {p_(gi.at[d, 'padj_exp_bh'])}" for d in ("up", "down") if d in gi.index))
        e_cells[f"{s}|{eid}"] = dict(t="cat", v={"not_tested": "nt"}.get(call, call), tip=tip)
    espec = dict(el="ecall", rows=a_rows, cols=ecols, cells=e_cells, blockLabel=BLOCK_LABEL, colLabels=True, cw=22, ch=22,
                 left=330, top=120)
    body = f"""<h1>Aggregated results: hli and the reference sets</h1>
<p class="lead">Per gene set: how many testable tests reach BH padj &lt; 0.05 in each reading scope, and the per-experiment calls. {DIRECTION_NOTE}</p>
<h2>By reading scope</h2>
<p class="note">Each cell: left half = tests significant up (orange, shade = share of testable tests), right half = significant down (blue);
n = testable tests. Light onset: treatment lit. Constant dark vs light: control lit. Schedule extension pools extended light (treatment lit)
and extended darkness (control lit), so its direction mixes lit arms. DCMU has no testable test and is not shown.</p>
<div class="wrap" style="max-height:none" id="agg"></div>
<p class="note">Static: <a href="../figures/aggregate_by_scope.png">aggregate_by_scope.png</a></p>
<h2>Per-experiment calls</h2>
<p class="note">Call per experiment and set: smallest testable time-point p × number of testable time points (cap 1), BH across experiments
per set, padj &lt; 0.05. Hatched = no testable time point. Hover for time-point counts.</p>
<div class="controls"><label>Column order <select id="eord"><option value="group">by light reading / experiment group</option>
<option value="light">by treatment-arm light level</option></select></label></div>
<div class="wrap" style="max-height:none" id="ecall"></div>
<p class="note">Static: <a href="../figures/experiment_calls_by_group.png">by group</a>, <a href="../figures/experiment_calls_by_light.png">by light level</a></p>
<h2>Resemblance table</h2><div class="controls"><input id="fr" placeholder="filter (set, scope)"></div>{table(res, "tr")}
<h2>Experiment calls (all sets)</h2>
<p class="note">Coculture HOT1A3 vs axenic (2025) keeps one experiment-level row; per decisions A.3–A.6 its day 11 is non-stress
(both arms exponential) and its day 18 is N stress from the control side (the axenic control is N-starving and dying). Its
per-time-point set-level calls are shown below the table.</p>
<div class="controls"><input id="fc" placeholder="filter"></div>
{table(calls[["label", "label_detailed", "display_note", "light_reading_group", "set", "set_role", "direction", "timepoint_count", "p_exp_bonferroni", "padj_exp_bh", "experiment_call", "experiment_id"]], "tc")}
<p class="note">Coculture HOT1A3 vs axenic (2025), per time point (set level, BH padj &lt; 0.05 among testable tests):</p>
{table(pt_calls, "tpc")}"""
    js = (f"const AS={json.dumps(aspec)};const ES={json.dumps(espec)};grid(AS,'group');wireGrid(ES,'eord');"
          "filterTable('fr','tr');filterTable('fc','tc');")
    (REP / "aggregate.html").write_text(page("Aggregated results", "Per gene set and reading scope: tests significant up and down, plus per-experiment calls, for hli and all reference sets.", body, js), encoding="utf-8")

    # ---------------- light_readings.html (pt_calls defined before aggregate page below)
    body = f"""<h1>Light readings</h1>
<p class="lead">hli read by the light rules fixed before hli was scored (methods notebook). {DIRECTION_NOTE}</p>
<ul class="note"><li>light onset (treatment lit): up = up with light</li><li>constant dark vs light (control lit): down = up with light</li>
<li>schedule extension: raw hli direction in extended darkness 2 h vs extended light 14 h; same = schedule response, opposite = light
response, otherwise unclear; 4 h / 16 h pair (flagged genome-wide) shown as context only</li><li>DCMU and phage in the dark: gene-level counts only</li></ul>
<p class="note">set_direction_raw: which directions have a testable hli test with BH padj &lt; 0.05 (not_testable = neither direction testable).</p>
{table(lr[["light_reading_group", "row_type", "label", "label_detailed", "more_light_arm", "timepoint", "set_direction_raw", "hli_up_n_sig", "hli_up_padj", "hli_up_flags", "hli_down_n_sig", "hli_down_padj", "hli_down_flags", "hli_measured", "genes_up", "genes_down", "genes_ns", "genes_not_measured", "groups_measured", "groups_up", "groups_down", "reading", "rule"]], "tl")}"""
    (REP / "light_readings.html").write_text(page("Light readings", "hli in the light experiments, read with the fixed light rules (light onset, constant dark vs light, schedule extension, DCMU, phage dark).", body), encoding="utf-8")

    # ---------------- summary.html
    hs_ = h[h.testable]
    facts = pd.DataFrame([
        ("hli tests (experiment × timepoint × direction)", len(h)),
        ("hli testable tests", int(h.testable.sum())),
        ("hli tests with BH padj < 0.05: up / down", f"{int(((hs_.padj_bh < 0.05) & (hs_.direction == 'up')).sum())} / {int(((hs_.padj_bh < 0.05) & (hs_.direction == 'down')).sum())}"),
        ("hli experiment calls: up / down / both / neither / not tested",
         " / ".join(str(int((calls[(calls.set == 'hli')].drop_duplicates('experiment_id').experiment_call == c).sum()))
                    for c in ["up", "down", "both", "neither", "not_tested"])),
        ("hli gene × experiment × timepoint calls: up / down / ns / not measured",
         " / ".join(str(int((gc.call == c).sum())) for c in ["up", "down", "ns", "not_measured"])),
        ("Testable hli tests with empirical p (random sets) ≤ 0.05", int((rb[rb.testable == True].empirical_p_random <= 0.05).sum())),
        ("BH recompute (statsmodels) max |Δ| over 13 sets", f"{qcbh[qcbh.check.str.startswith('bh_')].max_abs_diff.max():.1e}"),
        ("Reference rows vs methods control_tests: max |Δ padj|", f"{qcbh[qcbh.check == 'reference_vs_methods:padj_bh'].max_abs_diff.iloc[0]:.1e}"),
        ("Random sets vs methods: max |Δ p|", f"{qcbh[qcbh.check == 'random_sets_vs_methods:pvalue'].max_abs_diff.iloc[0]:.1e}"),
        ("hli genes in main background, min–max per test", f"{cov.hli_in_background.min()}–{cov.hli_in_background.max()}"),
    ], columns=["Item", "Value"])
    files = sorted([f"../data/{p.name}" for p in DATA.glob("*.csv")] + [f"../scripts/{p.name}" for p in (ANALYSIS / "scripts").glob("*.py")]
                   + [f"../figures/{p.name}" for p in FIG.glob("*.png")])
    body = f"""<h1>Analysis part A (MED4) — summary</h1>
<p class="lead">hli scored with the approved methods pipeline. Counts only; meanings are in the analysis notebook. All results exploratory.</p>
<p class="note">Display decisions A.3–A.6: Coculture HOT1A3 vs axenic (2025) is shown per time point (day 11 non-stress, both
exponential; day 18 N stress from the control side); its experiment-level call stays one row ("day 11 non-stress; day 18 N stress
from the control side; see A.3–A.6"). PRO99-lowN starvation labels add "vs the same culture in exponential growth (day 11)".
Labels and grouping only; no test changed.</p>
<h2>What this milestone asked</h2>{codefine()}
<h2>Run facts</h2>{table(facts)}
<h2>Pages</h2><ul><li><a href="hli_heatmaps.html">hli heatmaps</a> — gene-level and set-level heatmaps, hli tests, random baseline, gene calls</li>
<li><a href="aggregate.html">Aggregated results</a> — per set × reading scope, per-experiment calls, resemblance table</li>
<li><a href="light_readings.html">Light readings</a> — the fixed light rules applied to hli</li>
<li><a href="explore.html">Exploration</a> — A gene families, B light level, C timing (built by 07_build_explore_report.py)</li></ul>
<h2>QC</h2>{table(qcbh)}<p class="note">hli coverage per experiment × timepoint:</p>{table(cov)}
<p class="note">Sign distribution of full DE tables:</p>{table(sign)}<p class="note">DE row checks:</p>{table(qcde)}
<h2>Files</h2><ul>{''.join(f'<li><a href="{f}">{html.escape(f)}</a></li>' for f in files)}</ul>"""
    (REP / "summary.html").write_text(page("Analysis summary", "Analysis part A (MED4): hli scored in 29 experiments; run facts, QC and links (no interpretation).", body), encoding="utf-8")
    print("wrote", sorted(p.name for p in REP.glob("*.html")))


if __name__ == "__main__":
    main()
