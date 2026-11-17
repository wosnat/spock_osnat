"""Build analysis/reports/explore.html (exploration A families, B light level, C timing) from analysis/data/explore_*.csv.

Reuses the page, table and grid helpers of analysis/scripts/build_reports.py. Counts and facts only.

Run from the repo root (after 04, 05, 06):
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/07_build_explore_report.py
"""
import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("br", HERE / "build_reports.py")
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)
DATA, REP = br.DATA, br.REP


D_PANELS_JS = r"""
const SYM={o:(x,y,r)=>`<circle cx="${x}" cy="${y}" r="${r}"/>`,
 s:(x,y,r)=>`<rect x="${x-r}" y="${y-r}" width="${2*r}" height="${2*r}"/>`,
 '^':(x,y,r)=>`<path d="M${x},${y-r*1.2}L${x+r*1.1},${y+r*.8}L${x-r*1.1},${y+r*.8}Z"/>`,
 v:(x,y,r)=>`<path d="M${x},${y+r*1.2}L${x+r*1.1},${y-r*.8}L${x-r*1.1},${y-r*.8}Z"/>`,
 D:(x,y,r)=>`<path d="M${x},${y-r*1.3}L${x+r},${y}L${x},${y+r*1.3}L${x-r},${y}Z"/>`,
 P:(x,y,r)=>`<path d="M${x-r*.4},${y-r}h${r*.8}v${r*.6}h${r*.6}v${r*.8}h${-r*.6}v${r*.6}h${-r*.8}v${-r*.6}h${-r*.6}v${-r*.8}h${r*.6}Z"/>`,
 X:(x,y,r)=>`<path d="M${x-r},${y-r}L${x+r},${y+r}M${x+r},${y-r}L${x-r},${y+r}" stroke-width="2.2"/>`,
 h:(x,y,r)=>`<path d="M${x-r},${y}L${x-r/2},${y-r*.9}L${x+r/2},${y-r*.9}L${x+r},${y}L${x+r/2},${y+r*.9}L${x-r/2},${y+r*.9}Z"/>`};
function dpanels(spec){
 const ink=css('--ink'),mut=css('--muted'),rule=css('--rule');const pw=250,ph=180,m={l:38,r:8,t:30,b:22},nc=5;
 const genes=spec.genes,W=nc*pw,H=Math.ceil(genes.length/nc)*ph;
 let s=`<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" font-size="9" font-family="system-ui">`;const tips=[];
 const fx=spec.logx?(v=>Math.log10(v)):(v=>v);const x0=fx(spec.xmin),x1=fx(spec.xmax);
 genes.forEach((g,k)=>{const ox=(k%nc)*pw,oy=Math.floor(k/nc)*ph,iw=pw-m.l-m.r,ih=ph-m.t-m.b;
  const P=spec.points.filter(p=>p.g===g.g);if(!P.length)return;
  let y0=Math.min(0,...P.map(p=>p.y)),y1=Math.max(0,...P.map(p=>p.y));const pad=(y1-y0)*0.08||1;y0-=pad;y1+=pad;
  const X=v=>ox+m.l+(fx(v)-x0)/(x1-x0)*iw,Y=v=>oy+m.t+(1-(v-y0)/(y1-y0))*ih;
  s+=`<rect x="${ox+m.l}" y="${oy+m.t}" width="${iw}" height="${ih}" fill="none" stroke="${g.col}" stroke-width="1.4"/>`;
  s+=`<text x="${ox+m.l}" y="${oy+12}" fill="${g.col}" font-size="9.5">${esc(g.title)}</text>`;
  s+=`<line x1="${ox+m.l}" x2="${ox+m.l+iw}" y1="${Y(0)}" y2="${Y(0)}" stroke="${rule}"/>`;
  [y0,(y0+y1)/2,y1].forEach(v=>{s+=`<text x="${ox+m.l-3}" y="${Y(v)+3}" text-anchor="end" fill="${mut}" font-size="8">${v.toFixed(1)}</text>`});
  spec.xticks.forEach(v=>{s+=`<text x="${X(v)}" y="${oy+ph-8}" text-anchor="middle" fill="${mut}" font-size="8">${v}</text>`});
  if(spec.lines){const by={};P.forEach(p=>{(by[p.e]=by[p.e]||[]).push(p)});Object.values(by).forEach(a=>{if(a.length<2)return;a.sort((p,q)=>p.x-q.x);
    s+=`<polyline points="${a.map(p=>X(p.x)+','+Y(p.y)).join(' ')}" fill="none" stroke="${a[0].c}" stroke-width="1" opacity="0.85"/>`})}
  P.forEach(p=>{const i=tips.length;tips.push(p.tip);const f=p.sig?p.c:'white';
    s+=`<g class="dp" data-i="${i}" fill="${f}" stroke="${p.c}" stroke-width="1.1">${SYM[p.m](X(p.x),Y(p.y),3.6)}<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="7" fill="transparent" stroke="none"/></g>`})});
 s+='</svg>';const host=document.getElementById(spec.el);host.innerHTML=s;const tip=document.getElementById('tip');
 host.querySelectorAll('g.dp').forEach(el=>{el.addEventListener('mousemove',e=>{tip.innerHTML=tips[+el.dataset.i];tip.style.display='block';
  tip.style.left=Math.min(e.clientX+12,innerWidth-390)+'px';tip.style.top=(e.clientY+12)+'px'});el.addEventListener('mouseleave',()=>tip.style.display='none')})}
"""


def section_d():
    """Section D (response groups): interactive clustered grid, per-gene trajectories over time and light level."""
    import importlib.util as iu
    sp = iu.spec_from_file_location("traj", HERE / "10_explore_gene_trajectories.py")
    traj = iu.module_from_spec(sp)
    sp.loader.exec_module(traj)
    cl = br.read("explore_D_gene_clusters.csv").sort_values("leaf_order")
    par = br.read("explore_D_parameters.csv").iloc[0]
    rob = br.read("explore_D_cluster_robustness.csv")
    ckt = br.read("explore_D_cluster_ck.csv")
    summ = br.read("explore_D_cluster_summary.csv")
    co = br.read("explore_D_column_order.csv")
    unp = br.read("explore_D_unparsed_timepoints.csv")
    M = pd.read_csv(DATA / "explore_D_matrix.csv", encoding="utf-8", index_col=0)
    pts = br.read("explore_D_trajectory_points.csv")
    ccol = traj.CLUSTER_COL
    info = cl.set_index("locus_tag")
    rows = [dict(k=r.locus_tag, label=f"{r.locus_tag} {r.ck_group} {'■' if r.copy_class == 'multi' else '□'}",
                 band=f"C{r.cluster}") for r in cl.itertuples()]
    cols = [dict(k=c, label=lab, detail=f"{lab} · {tp}", block="all", rank=i, light=0, lightc=0, sub=0)
            for i, (c, lab, tp) in enumerate(zip(co.col, co.label_detailed, co.timepoint))]
    pidx = pts.assign(col=pts.experiment_id + "|" + pts.timepoint).set_index(["locus_tag", "col"])
    cells = {}
    for g in M.index:
        for c in co.col:
            v = M.at[g, c]
            r = pidx.loc[(g, c)]
            kind = "nm" if pd.isna(v) else {1.0: "up", -1.0: "down", 0.0: "ns"}[float(v)]
            cells[f"{g}|{c}"] = dict(t="cat", v=kind, tip=(
                f"<b>{g}</b> ({br.html.escape(info.at[g, 'ck_group'])}, C{info.at[g, 'cluster']})<br>"
                f"{br.html.escape(r.label_detailed)} · {br.html.escape(r.timepoint)}<br>call: <b>{r.call}</b>"
                f"{' (not defined in clustering)' if pd.isna(v) else ''}<br>log2FC {br.p_(r.log2fc)} · padj {br.p_(r.padj)}"))
    d1 = dict(el="d1", rows=rows, cols=cols, cells=cells, blockLabel={"all": " "}, colLabels=True, left=230, top=40, lb=430)

    def tipp(r):
        return (f"<b>{r.locus_tag}</b> ({br.html.escape(r.ck_group)}, C{r.cluster})<br>{br.html.escape(r.label_detailed)}"
                f"<br>stress type: {r.stress_type}<br>time point: {br.html.escape(r.timepoint)}"
                f"{'' if pd.isna(r.hours) else f' ({r.hours:g} h)'}<br>log2FC {br.p_(r.log2fc)} · padj {br.p_(r.padj)}"
                f"<br>call: {r.call} · test type: {r.test_type}<br>background light {r.light_control_umol:g} µmol")
    genes = [dict(g=r.locus_tag, col=ccol[r.cluster], title=f"C{r.cluster} · {r.locus_tag} · {r.ck_group} ({r.copy_class})")
             for r in cl.itertuples()]
    p2 = [dict(g=r.locus_tag, e=r.experiment_id, x=float(r.hours_plot), y=float(r.log2fc), sig=bool(r.significant),
               c=traj.STYLE[r.category][0], m=traj.STYLE[r.category][1], tip=tipp(r))
          for r in pts[pts.hours.notna() & pts.log2fc.notna()].itertuples()]
    p3 = [dict(g=r.locus_tag, e=r.experiment_id, x=float(r.light_control_umol), y=float(r.log2fc), sig=bool(r.significant),
               c=traj.STYLE[r.category][0], m=traj.STYLE[r.category][1], tip=tipp(r))
          for r in pts[pts.continuous_light & pts.log2fc.notna()].itertuples()]
    d2 = dict(el="d2", genes=genes, points=p2, logx=True, xmin=0.07, xmax=3000, xticks=[0.1, 1, 10, 100, 1000], lines=True)
    d3 = dict(el="d3", genes=genes, points=p3, logx=False, xmin=0, xmax=100, xticks=[0, 20, 40, 60, 80, 100], lines=False)
    leg = " ".join(f'<span style="color:{c}">{"●■▲◆▼✚✖⬢"["os^DvPXh".index(m)]}</span> {k}' for k, (c, m) in traj.STYLE.items())
    html_ = f"""<h2>D. Response groups of the 23 hli genes</h2>
<p class="note">Genes × {int(par.n_columns)} experiment-time-point columns; value = published call (+1 up, 0 not significant, −1 down).
Not defined (hatched): not measured; non-significant genes in the up-only phage array; phosphate 0–24 h genes absent from a table filtered
at 48 h. Dropped columns: pooled "days 60+89" and the phage array 2–8 h columns (no defined value). Fold changes are not used for
clustering: they are not comparable across microarray and RNA-seq, and significant-only tables give none for non-significant genes.
Distance = 1 − agreement over cells defined in both genes (≥{int(par.min_shared)} shared, else 1); average linkage; cut at
{float(par.cut_height_agreement):.3f} → {int(par.k)} clusters. Columns clustered the same way. ■ multi-copy CK group, □ single-copy.</p>
<img src="../figures/explore_D1_clustered_heatmap.png" alt="Clustered heatmap of hli calls">
<p class="note">Interactive (rows and columns in the clustered order; hover for call, log2FC, padj):</p>
<div class="wrap" style="max-height:none" id="d1"></div>
<p class="note">Cluster membership and robustness (correlation distance = (1 − Pearson r)/2 on shared cells, cut at
{float(par.cut_height_correlation):.3f}; and agreement without the six Steglich 2006 light-shift columns, cut at
{float(par.cut_height_no_steglich):.3f}; cluster labels matched to the primary clustering):</p>{br.table(rob, "td1")}
<p class="note">CK-group make-up per cluster (near-identical multi-copy paralogs may share array probes or multi-mapping reads, so
members of the same CK group can co-cluster for technical reasons):</p>{br.table(ckt, "td2")}
<p class="note">Per cluster × category: % of measured (defined) cells up and down:</p>{br.table(summ, "td3")}
<h3>D2. Over time (published log2FC; x = hours since treatment start, log)</h3>
<p class="note">Colour and marker = stress type: {leg}. Filled = significant, hollow = not significant; significant-only tables report only
significant genes. Heights are not comparable across platforms: read only shape and timing within an experiment. 0 h shown at 0.1 h.
Panel border / title colour = cluster. Hover any point.</p>
<div class="wrap" style="max-height:none" id="d2"></div>
<p class="note">Static: <a href="../figures/explore_D2_time_log2fc.png">log2FC over time</a>, <a href="../figures/explore_D2b_time_calls.png">calls over time</a>.
Time points not on the axis (not a time):</p>{br.table(unp, "td4")}
<h3>D3. Versus background light level (18 continuous-light experiments)</h3>
<p class="note">Cells are acclimated to the background light before the treatment, and DE measures change vs a control at that same
light, so light level here is context, not a treatment; cross-study, so platform, design and stress are confounded. Same colours,
markers and filling as D2.</p>
<div class="wrap" style="max-height:none" id="d3"></div>
<p class="note">Static: <a href="../figures/explore_D3_light_level.png">explore_D3_light_level.png</a></p>"""
    js_ = D_PANELS_JS + (f"const D1={json.dumps(d1)};grid(D1,'group');const D2={json.dumps(d2)};const D3={json.dumps(d3)};"
                         "dpanels(D2);dpanels(D3);")
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
