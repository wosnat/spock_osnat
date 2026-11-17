"""Build analysis/reports/explore.html (exploration A families, B light level, C timing) from analysis/data/explore_*.csv.

Reuses the page, table and grid helpers of analysis/scripts/build_reports.py. Counts and facts only.

Run from the repo root (after 04, 05, 06):
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/07_build_explore_report.py
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d_scheme as ds  # noqa: E402
spec = importlib.util.spec_from_file_location("br", HERE / "build_reports.py")
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)
DATA, REP = br.DATA, br.REP


D_JS = r"""
const SYM={o:(x,y,r)=>`<circle cx="${x}" cy="${y}" r="${r}"/>`,
 s:(x,y,r)=>`<rect x="${x-r}" y="${y-r}" width="${2*r}" height="${2*r}"/>`,
 '^':(x,y,r)=>`<path d="M${x},${y-r*1.2}L${x+r*1.1},${y+r*.8}L${x-r*1.1},${y+r*.8}Z"/>`,
 v:(x,y,r)=>`<path d="M${x},${y+r*1.2}L${x+r*1.1},${y-r*.8}L${x-r*1.1},${y-r*.8}Z"/>`,
 D:(x,y,r)=>`<path d="M${x},${y-r*1.3}L${x+r},${y}L${x},${y+r*1.3}L${x-r},${y}Z"/>`,
 P:(x,y,r)=>`<path d="M${x-r*.4},${y-r}h${r*.8}v${r*.6}h${r*.6}v${r*.8}h${-r*.6}v${r*.6}h${-r*.8}v${-r*.6}h${-r*.6}v${-r*.8}h${r*.6}Z"/>`};
const CALLCOL={up:'#eb6834',down:'#2a78d6',ns:'#d9d8d4'};
function hov(host,sel,tips){const tip=document.getElementById('tip');host.querySelectorAll(sel).forEach(el=>{
 el.addEventListener('mousemove',e=>{tip.innerHTML=tips[+el.dataset.i];tip.style.display='block';
  tip.style.left=Math.min(e.clientX+14,innerWidth-400)+'px';tip.style.top=(e.clientY+14)+'px'});
 el.addEventListener('mouseleave',()=>tip.style.display='none')})}
// D1-style heatmap: spec {el, rows:[{k,label,band}], cols:[{k,short,colour,major,minor,majorLabel}], cells:{r|c:{v,tip}}}
function dheat(spec){
 const ink='#1f1f1d',mut='#6b6b66',cw=spec.cw||17,ch=spec.ch||19,left=spec.left||250,top=spec.top||70,lb=spec.lb||120;
 const rows=spec.rows,cols=spec.cols,W=left+cols.length*cw+20,H=top+rows.length*ch+lb;const tips=[];
 let s=`<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" font-family="system-ui" font-size="11">`;
 if(spec.title)s+=`<text x="6" y="18" font-weight="bold" fill="${ink}" font-size="12">${esc(spec.title)}</text>`;
 s+=`<defs><pattern id="hh_${spec.el}" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="4" stroke="#b5b4ae" stroke-width="1"/></pattern></defs>`;
 rows.forEach((r,i)=>{const y=top+i*ch;if(i===0||rows[i-1].band!==r.band){s+=`<text x="6" y="${y+13}" font-weight="bold" fill="${ink}">${esc(r.band)}</text>`;
   if(i>0)s+=`<line x1="4" x2="${left+cols.length*cw}" y1="${y}" y2="${y}" stroke="${ink}" stroke-width="2"/>`}
   s+=`<text x="${left-6}" y="${y+ch/2+4}" text-anchor="end" fill="${ink}">${esc(r.label)}</text>`});
 cols.forEach((c,j)=>{const x=left+j*cw;s+=`<rect x="${x}" y="${top-14}" width="${cw-1}" height="10" fill="${c.colour}"/>`;
   if(j>0&&c.major!==cols[j-1].major)s+=`<line x1="${x}" x2="${x}" y1="${top-40}" y2="${top+rows.length*ch}" stroke="${ink}" stroke-width="2"/>`;
   else if(j>0&&c.minor!==cols[j-1].minor)s+=`<line x1="${x}" x2="${x}" y1="${top-4}" y2="${top+rows.length*ch}" stroke="${mut}" stroke-width="0.8"/>`;
   s+=`<text transform="translate(${x+cw/2+4},${top+rows.length*ch+6}) rotate(90)" fill="${ink}" font-size="10">${esc(c.short)}</text>`});
 let st=0;for(let j=1;j<=cols.length;j++){if(j===cols.length||cols[j].major!==cols[st].major){const n=j-st,x=left+(st+j)/2*cw,t=cols[st].majorLabel;
   s+=n*cw>t.length*6.2?`<text x="${x}" y="${top-24}" text-anchor="middle" font-weight="bold" fill="${ink}" font-size="10">${esc(t)}</text>`
     :`<text transform="translate(${x+4},${top-20}) rotate(-90)" font-weight="bold" fill="${ink}" font-size="9">${esc(t)}</text>`;st=j}}
 rows.forEach((r,i)=>cols.forEach((c,j)=>{const cell=spec.cells[r.k+'|'+c.k];if(!cell)return;const x=left+j*cw,y=top+i*ch,k=tips.length;tips.push(cell.tip);
   const f=cell.v==='nd'?`url(#hh_${spec.el})`:CALLCOL[cell.v];
   s+=`<rect class="hc" data-i="${k}" x="${x+0.5}" y="${y+0.5}" width="${cw-1.5}" height="${ch-1.5}" fill="${f}" stroke="${cell.v==='nd'?'#e4e3df':'none'}"/>`}));
 s+='</svg>';const host=document.getElementById(spec.el);host.innerHTML=s;hov(host,'rect.hc',tips)}
// small multiples with fixed y (-100..100): spec {el, panels:[{title,colour,header}], series, logx, xmin, xmax, xticks, xlab, nc}
function dmult(spec){
 const ink='#1f1f1d',mut='#6b6b66',rule='#d9d8d4',pw=spec.pw||300,ph=spec.ph||270,m={l:44,r:30,t:34,b:36},nc=spec.nc||3;const tips=[];
 const W=nc*pw,H=Math.ceil(spec.panels.length/nc)*ph;let s=`<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" font-family="system-ui" font-size="10">`;
 const fx=spec.logx?Math.log10:(v=>v);
 spec.panels.forEach((p,k)=>{const ox=(k%nc)*pw,oy=Math.floor(k/nc)*ph,iw=pw-m.l-m.r,ih=ph-m.t-m.b;
  const xmin=p.xmin??spec.xmin,xmax=p.xmax??spec.xmax,X=v=>ox+m.l+(fx(v)-fx(xmin))/(fx(xmax)-fx(xmin))*iw,Y=v=>oy+m.t+(1-(v+100)/200)*ih;
  s+=`<rect x="${ox+m.l}" y="${oy+6}" width="${iw}" height="18" fill="${p.colour}"/><text x="${ox+m.l+5}" y="${oy+19}" fill="${p.headerInk||'white'}" font-weight="bold">${esc(p.title)}</text>`;
  s+=`<rect x="${ox+m.l}" y="${oy+m.t}" width="${iw}" height="${ih}" fill="none" stroke="${p.border||rule}" stroke-width="${p.border?1.5:1}"/>`;
  [-100,-50,0,50,100].forEach(v=>{s+=`<line x1="${ox+m.l}" x2="${ox+m.l+iw}" y1="${Y(v)}" y2="${Y(v)}" stroke="${v===0?mut:'#eeede9'}"/>`;
    s+=`<text x="${ox+m.l-4}" y="${Y(v)+3}" text-anchor="end" fill="${mut}" font-size="9">${Math.abs(v)}</text>`});
  s+=`<text x="${ox+m.l-30}" y="${Y(55)}" fill="${mut}" font-size="8" transform="rotate(-90 ${ox+m.l-30} ${Y(55)})">up %</text><text x="${ox+m.l-30}" y="${Y(-25)}" fill="${mut}" font-size="8" transform="rotate(-90 ${ox+m.l-30} ${Y(-25)})">down %</text>`;
  (p.xticks||spec.xticks).forEach(v=>{s+=`<text x="${X(v)}" y="${oy+m.t+ih+13}" text-anchor="middle" fill="${mut}" font-size="9">${v===0.1&&spec.logx?0:v}</text>`});
  s+=`<text x="${ox+m.l+iw/2}" y="${oy+ph-6}" text-anchor="middle" fill="${mut}" font-size="9">${esc(spec.xlab)}</text>`;
  (spec.series[k]||[]).forEach(se=>{if(se.line&&se.pts.length>1)s+=`<polyline points="${se.pts.map(q=>X(q.x)+','+Y(q.y)).join(' ')}" fill="none" stroke="${ink}" stroke-width="1.3" stroke-dasharray="${se.dash}"/>`;
    se.pts.forEach(q=>{const i=tips.length;tips.push(q.tip);s+=`<g class="mp" data-i="${i}" fill="${q.fill}" stroke="${q.stroke}" stroke-width="1">${SYM[q.m](X(q.x),Y(q.y),4)}<circle cx="${X(q.x)}" cy="${Y(q.y)}" r="8" fill="transparent" stroke="none"/></g>`});
    if(se.label&&se.pts.length){const q=se.pts[se.pts.length-1];s+=`<text x="${X(q.x)+7}" y="${Y(se.ly??q.y)+3}" fill="${ink}" font-size="9">${se.label}</text>`}})});
 s+='</svg>';const host=document.getElementById(spec.el);host.innerHTML=s;hov(host,'g.mp',tips)}
function dview(v){document.getElementById('d1a').style.display=v==='cluster'?'':'none';document.getElementById('d1b').style.display=v==='category'?'':'none'}
"""


def _shape(m, c, dx=0):
    x = 7 + dx
    return {"o": f'<circle cx="{x}" cy="7" r="5" fill="{c}"/>',
            "s": f'<rect x="{x - 5}" y="2" width="10" height="10" fill="{c}"/>',
            "^": f'<path d="M{x},1L{x + 6},12L{x - 6},12Z" fill="{c}"/>',
            "v": f'<path d="M{x},13L{x + 6},2L{x - 6},2Z" fill="{c}"/>',
            "D": f'<path d="M{x},0L{x + 6},7L{x},14L{x - 6},7Z" fill="{c}"/>',
            "P": f'<path d="M{x - 2},1h4v4h4v4h-4v4h-4v-4h-4v-4h4Z" fill="{c}"/>'}[m]


def legend_html(types_present=None, clusters=None):
    """Grouped family legend (shade + marker) and cluster key, inline SVG + text (visible without hover)."""
    out = ['<div class="legend-d">']
    for fam in ds.FAMILY_ORDER:
        items = [(t, c, m) for (f, t), (c, m) in ds.TYPES.items() if f == fam and (types_present is None or (f, t) in types_present)]
        if items:
            out.append(f"<div><b>{fam}</b>: " + " ".join(
                f'<span style="white-space:nowrap;margin-right:10px"><svg width="14" height="14" style="vertical-align:middle">'
                f'{_shape(m, c)}</svg> {t}</span>' for t, c, m in items) + "</div>")
    if clusters:
        parts = []
        for k in clusters:
            parts.append(f'<span style="white-space:nowrap;margin-right:12px"><svg width="44" height="14" style="vertical-align:middle">'
                         f'<line x1="2" x2="42" y1="7" y2="7" stroke="#1f1f1d" stroke-width="1.5" stroke-dasharray="{ds.CLUSTER_DASH[k]}"/>'
                         f'{_shape(ds.CLUSTER_STYLE[k][1], "#1f1f1d", 15)}</svg> C{k}</span>')
        out.append("<div><b>gene clusters</b> (ink; line style + marker + label): " + " ".join(parts)
                   + " · filled marker = % up (above 0), open marker = % down (below 0)</div>")
    out.append("</div>")
    return chr(10).join(out)


def section_d():
    """Section D (response groups): D1 interactive heatmap (cluster / category views), D2 cluster time courses,
    D3 cluster vs background light, each with a gene-level companion heatmap. Light theme, shared d_scheme colours."""
    cl = br.read("explore_D_gene_clusters.csv").sort_values("leaf_order")
    par = br.read("explore_D_parameters.csv").iloc[0]
    rob = br.read("explore_D_cluster_robustness.csv")
    ckt = br.read("explore_D_cluster_ck.csv")
    summ = br.read("explore_D_cluster_summary.csv")
    co = br.read("explore_D_column_order.csv")
    ccl = br.read("explore_D_column_clusters.csv")
    unp = br.read("explore_D_unparsed_timepoints.csv")
    M = pd.read_csv(DATA / "explore_D_matrix.csv", encoding="utf-8", index_col=0)
    pts = br.read("explore_D_trajectory_points.csv")
    cr = br.read("explore_D_cluster_response.csv")
    tce = br.read("explore_D_timecourse_experiments.csv")
    info = cl.set_index("locus_tag")
    ks = sorted(cl.cluster.unique())
    rows = [dict(k=r.locus_tag, label=f"{r.locus_tag}  {r.ck_group}  {'■ multi' if r.copy_class == 'multi' else '□ single'}",
                 band=f"C{r.cluster}") for r in cl.itertuples()]
    pidx = pts.set_index(["locus_tag", "experiment_id", "timepoint"])

    def cell_tip(g, e, tp):
        r = pidx.loc[(g, e, tp)]
        return (f"<b>{g}</b> · {br.html.escape(info.at[g, 'ck_group'])} · {info.at[g, 'copy_class']}-copy · cluster C{info.at[g, 'cluster']}"
                f"<br>{br.html.escape(r.label_detailed)}<br>time point: {br.html.escape(tp)}<br>category: {r.family} — {r.type}"
                f"<br>call: <b>{r.call}</b>{'' if r.up_defined else ' (not defined)'}<br>log2FC {br.p_(r.log2fc)} · padj {br.p_(r.padj)}")

    def cell_value(g, e, tp):
        r = pidx.loc[(g, e, tp)]
        if not r.up_defined or (r.call != "up" and not r.down_defined):
            return "nd"
        return r.call

    # D1 view a: clustered columns, column-cluster dividers
    co["family"] = co.family.fillna("")
    cols_a = [dict(k=f"{e}|{tp}", short=s_, colour=ds.TYPES[(f, t)][0], major=f"K{k}" if k else "K0",
                   minor=f"K{k}", majorLabel=(f"K{k}" if k else "K0 sparse"))
              for e, tp, s_, f, t, k in zip(co.experiment_id, co.timepoint, co.short, co.family, co.type, co.col_cluster)]
    # D1 view b: by category (family -> type -> experiment -> time)
    cb = co.copy()
    cb["fr"] = [ds.FAMILY_ORDER.index(f) for f in cb.family]
    cb["tr"] = [ds.type_rank(f, t) for f, t in zip(cb.family, cb.type)]
    tpo = pts.drop_duplicates(["experiment_id", "timepoint"]).set_index(["experiment_id", "timepoint"]).timepoint_order
    cb["to"] = [tpo.get((e, t), 0) for e, t in zip(cb.experiment_id, cb.timepoint)]
    cb = cb.sort_values(["fr", "tr", "label", "to"])
    cols_b = [dict(k=f"{e}|{tp}", short=s_, colour=ds.TYPES[(f, t)][0], major=f"{f}: {t}", minor=e, majorLabel=t)
              for e, tp, s_, f, t in zip(cb.experiment_id, cb.timepoint, cb.short, cb.family, cb.type)]
    cells = {}
    for g in M.index:
        for e, tp in zip(co.experiment_id, co.timepoint):
            cells[f"{g}|{e}|{tp}"] = dict(v=cell_value(g, e, tp), tip=cell_tip(g, e, tp))
    d1a = dict(el="d1a", rows=rows, cols=cols_a, cells=cells, left=270, top=70, lb=110)
    d1b = dict(el="d1b", rows=rows, cols=cols_b, cells=cells, left=270, top=70, lb=110)

    # D2: cluster response over time, per time-course experiment
    def resp_tip(r):
        return (f"<b>{br.html.escape(r.label_detailed)}</b><br>time point: {br.html.escape(r.timepoint)}"
                f"{'' if pd.isna(r.hours) else f' ({r.hours:g} h)'}<br>cluster C{r.cluster}: up {r.n_up} of {r.n_up_defined} defined, "
                f"down {r.n_down} of {r.n_down_defined} defined<br>up: {r.genes_up or '—'}<br>down: {r.genes_down or '—'}"
                f"<br>category: {r.family} — {r.type}; background light {r.light_umol:g} µmol")
    panels2, series2 = [], []
    for er in tce.itertuples():
        d = cr[cr.experiment_id == er.experiment_id].copy()
        d["xh"] = d.hours.replace(0, 0.1)
        xs = sorted(d.xh.dropna().unique())
        panels2.append(dict(title=f"{ds.SHORT.get(er.label, er.label)} · {er.type}", colour=ds.TYPES[(er.family, er.type)][0],
                            xmin=min(xs) / 1.6, xmax=max(xs) * 2.2, xticks=[float(x) for x in xs]))
        ser = []
        ends = []
        for k in ks:
            dk = d[(d.cluster == k) & d.xh.notna()].sort_values("xh")
            for yc, filled in (("pct_up", True), ("pct_down", False)):
                q = dk[dk[yc].notna()]
                ser.append(dict(line=True, dash=ds.CLUSTER_DASH[k], label=(f"C{k}" if yc == "pct_up" else ""),
                                pts=[dict(x=float(r.xh), y=float(getattr(r, yc)), m=ds.CLUSTER_STYLE[k][1],
                                          fill="#1f1f1d" if filled else "white", stroke="#1f1f1d", tip=resp_tip(r))
                                     for r in q.itertuples()]))
                if yc == "pct_up" and len(q):
                    ends.append([float(q.pct_up.iloc[-1]), len(ser) - 1])
        ends.sort()
        ly = [e_[0] for e_ in ends]
        for i in range(1, len(ly)):   # spread direct labels >= 14 % apart, keep inside -100..100
            ly[i] = max(ly[i], ly[i - 1] + 14)
        over = max(ly) - 100 if ly else 0
        if over > 0:
            ly = [v - over for v in ly]
        for (y0, idx), v in zip(ends, ly):
            ser[idx]["ly"] = v
        series2.append(ser)
    d2 = dict(el="d2", panels=panels2, series=series2, logx=True, xmin=0.07, xmax=3000, xticks=[], nc=3, pw=330,
              xlab="hours since treatment start (log; 0 h at 0.1)")
    # D2 companion heatmaps (one per experiment, genes x time)
    comp2 = []
    for er in tce.itertuples():
        g = pts[(pts.experiment_id == er.experiment_id) & pts.hours.notna()]
        tps = g[["timepoint", "hours"]].drop_duplicates().sort_values("hours").timepoint.tolist()
        el = "d2c_" + str(len(comp2))
        cc = {f"{gn}|{tp}": dict(v=cell_value(gn, er.experiment_id, tp), tip=cell_tip(gn, er.experiment_id, tp))
              for gn in M.index for tp in tps}
        comp2.append(dict(el=el, rows=rows, cols=[dict(k=tp, short=ds.short_tp(tp), colour=ds.TYPES[(er.family, er.type)][0],
                                                      major="all", minor=tp, majorLabel=" ")
                                                 for tp in tps], cells=cc, left=270, top=56, lb=70, cw=26, title=f"{er.label} · {er.type}"))
    # D3: cluster panels vs background light
    lc = cr[cr.continuous_light == True].copy()  # noqa: E712
    rng = np.random.default_rng(5)
    lc["xj"] = lc.light_umol + rng.uniform(-1.5, 1.5, len(lc))
    panels3, series3 = [], []
    for k in ks:
        d = lc[lc.cluster == k]
        panels3.append(dict(title=f"C{k} ({int((cl.cluster == k).sum())} genes)", colour="#ffffff", headerInk="#1f1f1d",
                            border="#1f1f1d"))
        ser = []
        for r in d.itertuples():
            c, mk = ds.TYPES[(r.family, r.type)]
            for yc in ("pct_up", "pct_down"):
                y = getattr(r, yc)
                if not pd.isna(y):
                    ser.append(dict(line=False, pts=[dict(x=float(r.xj), y=float(y), m=mk, fill=c, stroke="white", tip=resp_tip(r))]))
        series3.append(ser)
    d3 = dict(el="d3", panels=panels3, series=series3, logx=False, xmin=0, xmax=100, xticks=[0, 20, 40, 60, 80, 100], nc=4,
              pw=300, xlab="background light, µmol photons m⁻² s⁻¹ (both arms)")
    # D3 companion: genes x continuous-light experiment-timepoints ordered by light
    cc3 = pts[pts.continuous_light == True].drop_duplicates(["experiment_id", "timepoint"]).sort_values(  # noqa: E712
        ["light_control_umol", "label", "timepoint_order"])
    cols3 = [dict(k=f"{r.experiment_id}|{r.timepoint}", short=r.short, colour=ds.TYPES[(r.family, r.type)][0],
                  major=f"{r.light_control_umol:g}", minor=r.experiment_id, majorLabel=f"{r.light_control_umol:g} µmol")
             for r in cc3.itertuples()]
    cells3 = {f"{g}|{r.experiment_id}|{r.timepoint}": dict(v=cell_value(g, r.experiment_id, r.timepoint),
                                                          tip=cell_tip(g, r.experiment_id, r.timepoint))
              for g in M.index for r in cc3.itertuples()}
    d3c = dict(el="d3c", rows=rows, cols=cols3, cells=cells3, left=270, top=70, lb=110)

    types_all = None
    present2 = set(zip(tce.family, tce.type))
    present3 = set(zip(lc.family, lc.type))
    callkey = ('<div class="legend-d"><b>cells</b>: <span style="background:#eb6834;padding:0 8px"></span> up '
               '<span style="background:#2a78d6;padding:0 8px"></span> down <span style="background:#d9d8d4;padding:0 8px"></span> '
               'not significant <span style="background:repeating-linear-gradient(45deg,#b5b4ae 0 1px,#fff 1px 4px);padding:0 8px;'
               'border:1px solid #e4e3df"></span> not defined</div>')
    html_ = f"""<h2>D. Response groups of the 23 hli genes</h2>
<p class="note">Value per gene × experiment-time point = published call (up, down, not significant). Not defined (hatched): not measured;
non-significant genes in the up-only phage array; phosphate 0–24 h genes absent from a table filtered at 48 h. Pooled "days 60+89" and the
phage array 2–8 h columns (no defined value) are dropped: {int(par.n_columns)} columns. Fold changes are not used: they are not comparable
across microarray and RNA-seq, and significant-only tables give none for non-significant genes. Genes: distance = 1 − agreement over cells
defined in both (≥{int(par.min_shared)} shared, else 1), average linkage, cut at {float(par.cut_height_agreement):.3f} → {int(par.k)}
clusters C1–C{int(par.k)} (black dividers). Columns: the same distance; {int((co.col_cluster == 0).sum())} columns with fewer than
{int(par.min_shared)} defined genes are set apart as K0; the rest are cut at {float(ccl.cut_height_columns.iloc[0]):.3f} →
{int(ccl.k_col.iloc[0])} column clusters K1–K{int(ccl.k_col.iloc[0])}. ■ multi-copy CK group, □ single-copy. Hover any cell.</p>
<div class="controls"><label>Column order <select onchange="dview(this.value)"><option value="cluster">clustered (column clusters K)</option>
<option value="category">by category → experiment → time</option></select></label></div>
{legend_html(types_all)}{callkey}
<div class="wrap" style="max-height:none" id="d1a"></div><div class="wrap" style="max-height:none;display:none" id="d1b"></div>
<p class="note">Download: <a href="../figures/explore_D1_clustered_heatmap.png">static PNG</a> · <a href="../figures/explore_D1_clustered_heatmap.svg">SVG</a></p>
<p class="note">Column clusters (adjacent column pairs in clustered order: same experiment {float(ccl.adjacent_pairs_same_experiment_overall.iloc[0]):.3f},
same category {float(ccl.adjacent_pairs_same_category_overall.iloc[0]):.3f}, same time-point label {float(ccl.adjacent_pairs_same_timepoint_label_overall.iloc[0]):.3f};
per cluster: share of column pairs from the same experiment / category / family / time-point label):</p>
{br.table(ccl[["col_cluster", "n_columns", "n_experiments", "n_categories", "n_timepoint_labels", "share_pairs_same_experiment", "share_pairs_same_category", "share_pairs_same_family", "share_pairs_same_timepoint_label", "by_family", "by_category", "by_experiment", "columns", "note"]], "tdk")}
<p class="note">Gene clusters and robustness (correlation distance (1 − Pearson r)/2, cut at {float(par.cut_height_correlation):.3f};
agreement without the six Steglich 2006 columns, cut at {float(par.cut_height_no_steglich):.3f}; labels matched to the primary clustering):</p>{br.table(rob, "td1")}
<p class="note">CK-group make-up per cluster (near-identical multi-copy paralogs may share array probes or multi-mapping reads):</p>{br.table(ckt, "td2")}
<p class="note">Per cluster × category: % of defined cells up and down:</p>{br.table(summ, "td3")}
<h3>D2. Gene clusters over time</h3>
<p class="note">One panel per time-course experiment with ≥3 parseable time points (header colour = category). y = % of each cluster's genes
called up (above 0, filled) and down (below 0, open); same −100…+100 axis in every panel. Denominator = genes with a defined call.
Lines are ink, told apart by line style, marker and the direct label. Hover any point for counts and locus tags.</p>
{legend_html(present2, ks)}
<div class="wrap" style="max-height:none" id="d2"></div>
<p class="note">Gene-level companion: genes (cluster order) × time points in time order, per experiment.</p>{callkey}
{''.join(f'<div class="wrap" style="max-height:none;display:inline-block;vertical-align:top;margin:0 6px 6px 0" id="{c["el"]}"></div>' for c in comp2)}
<p class="note">Download: <a href="../figures/explore_D2_cluster_time.png">clusters over time</a> · <a href="../figures/explore_D2_gene_time.png">gene-level time heatmaps</a>.
Time points not on a time axis (not a time):</p>{br.table(unp, "td4")}
<h3>D3. Gene clusters vs background light (18 continuous-light experiments)</h3>
<p class="note">One panel per gene cluster; each point = one experiment × time point, % of the cluster's genes up (above 0) and down (below 0);
colour + marker = category; same −100…+100 axis. Cells are acclimated to the background light before the treatment, and DE measures
change vs a control at that same light, so light level here is context, not a treatment; cross-study, so platform, design and stress are
confounded. x jittered ±1.5. Hover any point.</p>
{legend_html(present3)}
<div class="wrap" style="max-height:none" id="d3"></div>
<p class="note">Gene-level companion: genes (cluster order) × continuous-light experiment-time points ordered by light level.</p>{callkey}
<div class="wrap" style="max-height:none" id="d3c"></div>
<p class="note">Download: <a href="../figures/explore_D3_cluster_light.png">clusters vs light</a> · <a href="../figures/explore_D3_gene_light.png">gene-level heatmap</a></p>"""
    js_ = D_JS + (f"dheat({json.dumps(d1a)});dheat({json.dumps(d1b)});dmult({json.dumps(d2)});"
                  + "".join(f"dheat({json.dumps(c)});" for c in comp2)
                  + f"dmult({json.dumps(d3)});dheat({json.dumps(d3c)});")
    return html_, js_


def main():
    fam = br.read("explore_families.csv")
    fsc = br.read("explore_families_scope.csv")
    ll = br.read("explore_light_level.csv")
    sp = br.read("explore_light_level_spearman.csv")
    tm = br.read("explore_timing.csv")
    ts = br.read("explore_timing_summary.csv")
    tl = br.read("explore_timing_labels.csv")

    # A1 interactive: CK groups x experiment-timepoints, net share
    ck = fam[fam.family_type == "ck_group"]
    t = br.read("hli_tests.csv")
    cols = br.col_specs(t)
    size = ck.drop_duplicates("family").set_index("family")
    fams = sorted(size.index, key=lambda f: (-size.at[f, "family_size"], f))
    rows = [dict(k=f, label=f"{f} (n={size.at[f, 'family_size']}, {size.at[f, 'copy_class'].replace('_', '-')})",
                 band=("Multi-copy" if size.at[f, "copy_class"] == "multi_copy" else "Single-copy")) for f in fams]
    cells = {}
    for r in ck.itertuples():
        cells[f"{r.family}|{r.experiment_id}|{r.timepoint}"] = dict(
            t="net", nm=bool(r.n_measured == 0), v=0.0 if r.n_measured == 0 else float(r.net_share),
            tip=(f"<b>{r.family}</b> ({r.family_size} genes)<br>{br.html.escape(r.label_detailed)} · {br.html.escape(r.timepoint)}"
                 f"<br>measured {r.n_measured}: up {r.n_up}, down {r.n_down}<br>net share {br.p_(r.net_share)}"
                 f"<br>test type: {r.test_type}"))
    a1 = dict(el="a1", rows=rows, cols=cols, cells=cells, blockLabel=br.BLOCK_LABEL, colLabels=True, left=300, top=120)

    # B2 interactive: continuous-light experiments only (light_reading_group none), ordered by light level
    clx = br.read("explore_continuous_light_experiments.csv")
    keep = set(clx.experiment_id)
    t_cl = t[t.experiment_id.isin(keep)]
    cols_cl = br.col_specs(t_cl)
    gc = br.read("hli_gene_calls.csv")
    gc = gc[gc.experiment_id.isin(keep)]
    genes = gc[["locus_tag", "ck_group"]].drop_duplicates("locus_tag").sort_values(["ck_group", "locus_tag"])
    g_rows = [dict(k=r.locus_tag, label=f"{r.locus_tag} ({r.ck_group.replace('cyanorak:', '')})") for r in genes.itertuples()]
    g_cells = {f"{r.locus_tag}|{r.experiment_id}|{r.timepoint}": dict(
        t="cat", v={"not_measured": "nm"}.get(r.call, r.call),
        tip=(f"<b>{br.html.escape(r.locus_tag)}</b> ({br.html.escape(r.ck_group)})<br>{br.html.escape(r.label_detailed)} · "
             f"{br.html.escape(r.timepoint)}<br>light {r.light_treatment_umol:g} µmol (both arms)<br>call: <b>{r.call}</b> "
             f"({r.call_source})<br>log2FC {br.p_(r.log2fc)} · padj {br.p_(r.padj)}")) for r in gc.itertuples()}
    b2g = dict(el="b2g", rows=g_rows, cols=cols_cl, cells=g_cells, blockLabel=br.BLOCK_LABEL, colLabels=True, left=200, top=120)
    s_rows = [dict(k=f"{s}|{d}", label=f"{l} — {d}", band=b, dir=d) for s, l, b in br.SET_ROWS for d in ("up", "down")]
    s_cells = {}
    for r in t_cl.itertuples():
        fl = r.flags if isinstance(r.flags, str) else ""
        s_cells[f"{r.set}|{r.direction}|{r.experiment_id}|{r.timepoint}"] = dict(
            t="val", na=("not_testable" in fl or "descriptive" in fl), few=("too_few" in fl),
            v=(-br.np.log10(max(r.padj_bh, 1e-300)) if not br.np.isnan(r.padj_bh) else 0.0),
            sig=bool(r.padj_bh < 0.05) if not br.np.isnan(r.padj_bh) else False, gw="genome_wide" in fl,
            tip=(f"<b>{br.html.escape(r.set)}</b> · {r.direction}<br>{br.html.escape(r.label_detailed)} · "
                 f"{br.html.escape(r.timepoint)}<br>light {r.light_treatment_umol:g} µmol (both arms)<br>"
                 f"{br.fmt(r.n_sig_in_set)} of {r.n_measured_in_background} set genes significant<br>"
                 f"p {br.p_(r.pvalue)} · BH padj {br.p_(r.padj_bh)}<br>flags: {fl or 'none'}"))
    b2s = dict(el="b2s", rows=s_rows, cols=cols_cl, cells=s_cells, blockLabel=br.BLOCK_LABEL, colLabels=True, left=420, top=120)

    cc = fsc[fsc.family_type == "copy_class"]
    d_html, d_js = section_d()
    body = f"""<h1>Exploration: gene families, light level, timing</h1>
<p class="lead">MED4, hli genes. Exploratory. Treatment vs control as stored in the KG (no flip); the same significance calls as the
main analysis. Counts only; meanings are in the analysis notebook.</p>
<h2>A. Gene families</h2>
<p class="note">Copy class: CK groups with ≥2 MED4 hli members are multi-copy (CK_00002025, 2026, 2168, 2332, 43616: 14 genes); the 9
other groups have one member each (single-copy, 9 genes). Net share = (up − down) / measured members. Hatched = no member measured.
Descriptive time points are left out of the scope totals.</p>
<div class="controls"><label>Column order <select id="ordA"><option value="group">by light reading / experiment group</option>
<option value="light">by treatment-arm light level</option></select></label></div>
<div class="wrap" style="max-height:none" id="a1"></div>
<p class="note">Static: <a href="../figures/explore_A1_ck_groups_net.png">A1 CK groups</a></p>
<img src="../figures/explore_A2_copy_class.png" alt="Copy class: share of measured gene observations up and down per reading scope">
<p class="note">Copy class × reading scope:</p>{br.table(cc, "ta2")}
<p class="note">CK group × reading scope:</p><div class="controls"><input id="fa" placeholder="filter"></div>
{br.table(fsc[fsc.family_type == "ck_group"], "ta3")}
<p class="note">Per experiment × time point × family:</p><div class="controls"><input id="fa4" placeholder="filter"></div>
{br.table(fam[["family_type", "family", "copy_class", "family_size", "label", "timepoint", "test_type", "n_measured", "n_up", "n_down", "frac_up", "frac_down", "net_share", "experiment_id"]], "ta4")}
<h2>B. Light level</h2>
<p class="note">Non-light stress and non-stress experiments only (both arms at the same light). Cross-study comparison: light level is
confounded with platform, design and stress type. Spearman over testable tests, per direction, on unsigned −log10 BH padj and on the
share of the set significant.</p>
<img src="../figures/explore_B1_light_level.png" alt="Light level vs set-level result for hli and ribosomal proteins">
{br.table(sp, "tb1")}
<div class="controls"><input id="fb" placeholder="filter"></div>{br.table(ll, "tb2")}
<h2>B2. Continuous-light experiments only, ordered by light level</h2>
<p class="note">The 18 experiments with no light-reading role (non-light stress and non-stress); all 18 have light condition
"continuous light", both arms at the same level. Columns ordered by light level (block label); no day-night cycle and no light/dark
treatments. Same calls and colours as the main heatmaps. Hover for detail.</p>
{br.table(clx[["light_treatment_umol", "label", "group", "stress_type", "light_condition_raw", "experiment_id"]], "tb3")}
<p class="note">Gene level (23 hli genes):</p><div class="wrap" style="max-height:none" id="b2g"></div>
<p class="note">Set level (hli and all reference sets):</p><div class="wrap" style="max-height:none" id="b2s"></div>
<p class="note">Static: <a href="../figures/explore_B2_gene_heatmap_continuous_light_by_level.png">genes</a>,
<a href="../figures/explore_B2_set_band_continuous_light_by_level.png">sets</a>,
<a href="../figures/explore_B2_experiment_calls_continuous_light_by_level.png">per-experiment calls</a></p>
<img src="../figures/explore_B2_experiment_calls_continuous_light_by_level.png" alt="Per-experiment calls, continuous-light experiments, by light level">
<h2>C. Timing</h2>
<p class="note">Experiments with ≥3 time points on a time axis, plus extended light and extended darkness (2 time points each).
Time labels parsed to hours (h, min, day × 24); labels that are not a time are kept off the axis (listed below).
Filled points: hli set-level BH padj &lt; 0.05; open points: hli test not testable; dashed lines: descriptive table or time point.
Grey lines: ribosomal proteins.</p>
<img src="../figures/explore_C1_timing.png" alt="hli share up and down over time, per time-course experiment">
<p class="note">Per-experiment summary (hli):</p>{br.table(ts, "tc1")}
<img src="../figures/explore_C2_gene_time.png" alt="hli genes over time in four time courses">
<p class="note">Per time point, all sets:</p><div class="controls"><input id="fc" placeholder="filter (set, label)"></div>
{br.table(tm, "tc2")}
<p class="note">Time-label parsing (all experiment × time points; hours empty = kept off the time axis):</p>{br.table(tl, "tc3")}
{d_html}"""
    js = (d_js + f"const A1={json.dumps(a1)};wireGrid(A1,'ordA');"
          f"const B2G={json.dumps(b2g)};const B2S={json.dumps(b2s)};grid(B2G,'light');grid(B2S,'light');"
          "filterTable('fa','ta3');filterTable('fa4','ta4');filterTable('fb','tb2');filterTable('fc','tc2');")
    (REP / "explore.html").write_text(br.page("Exploration", "Exploration of hli in MED4: gene families (copy class), background light level, and timing in time-course experiments.", body, js), encoding="utf-8")
    print("wrote explore.html")


if __name__ == "__main__":
    main()
