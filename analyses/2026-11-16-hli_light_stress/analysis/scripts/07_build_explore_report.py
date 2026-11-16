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
<p class="note">Time-label parsing (all experiment × time points; hours empty = kept off the time axis):</p>{br.table(tl, "tc3")}"""
    js = (f"const A1={json.dumps(a1)};wireGrid(A1,'ordA');"
          f"const B2G={json.dumps(b2g)};const B2S={json.dumps(b2s)};grid(B2G,'light');grid(B2S,'light');"
          "filterTable('fa','ta3');filterTable('fa4','ta4');filterTable('fb','tb2');filterTable('fc','tc2');")
    (REP / "explore.html").write_text(br.page("Exploration", "Exploration of hli in MED4: gene families (copy class), background light level, and timing in time-course experiments.", body, js), encoding="utf-8")
    print("wrote explore.html")


if __name__ == "__main__":
    main()
