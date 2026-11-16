"""Plan step 2 infographic for overview.html.

Reads spike/step2_med4_inventory.csv (coverage only) and writes an HTML
fragment (stat tiles + one bar chart: hli genes measured per experiment,
coloured by test type) between the INFOGRAPHIC markers in overview.html.

Groups follow decisions_log step 2 (researcher agreed): the 4 glucose
proteomics experiments are dropped (no hli measured).

Run from the repo root:
    uv run python analyses/2026-11-16-hli_light_stress/spike/step2_infographic.py
"""
import html
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
CSV = HERE / "step2_med4_inventory.csv"
OVERVIEW = HERE.parent / "overview.html"
START, END = "<!-- INFOGRAPHIC START -->", "<!-- INFOGRAPHIC END -->"

df = pd.read_csv(CSV, encoding="utf-8")
df.loc[df.experiment_name.str.contains("glucose", case=False), "proposed_group"] = "dropped"
df.loc[df.omics_type == "PROTEOMICS", "proposed_group"] = "dropped"  # researcher: drop all proteomics
excluded = df[df.proposed_group.isin(["excluded", "dropped"])]
df = df[~df.proposed_group.isin(["excluded", "dropped"])].copy()

# Test type per the agreed rule (decisions_log): full table = sound;
# significance-filtered = approximate; top-N / expression filter = descriptive.
def test_type(r):
    if r.table_scope == "all_detected_genes":
        return "sound"
    if "Top 50%" in str(r.table_scope_detail):
        return "descriptive"
    return "approximate"

df["test_type"] = df.apply(test_type, axis=1)

OMICS = {"MICROARRAY": "array", "RNASEQ": "RNA-seq", "PROTEOMICS": "protein"}
SUBS = [
    (r"^MED4\s+", ""), (r"^proteomics:\s*", ""),
    (r"\s*\((MICROARRAY|RNASEQ|RNA-seq|iTRAQ|PROTEOMICS)\)\s*$", ""),
    (r"\s*\(MED4\)", ""), (r"\s*\([^)]*(%|m-2)[^)]*\)", ""),
    (r"umol photons m-2 s-1", "µmol"), (r"PRO99-lowN nutrient starvation vs PRO99-lowN exponential growth", "N starvation vs exponential"),
    (r"Phage \(P-HM2\) lysate vs Spent medium \(uninfected\) in (light|dark)", r"Phage lysate vs spent medium, \1"),
    (r"Phage infected vs uninfected spent-medium control", "Phage infected vs uninfected"),
    (r"vs Pro99 medium growth conditions", "vs medium alone"),
    (r"in coculture with HOT1A3,", "coculture,"), (r"Alteromonas HOT1A3", "Alteromonas"),
    (r"\s*Pro99 medium( growth conditions)?", ""), (r"Darkness control", "dark"), (r"\bvs\b", "vs"),
    (r"past (dusk|dawn) vs normal (dark|light) period", r"past \1"), (r"\s+", " "),
]

def short(r):
    s = r.experiment_name
    for pat, rep in SUBS:
        s = re.sub(pat, rep, s)
    s = s.strip()
    s = s if len(s) <= 44 else s[:43].rstrip() + "…"
    return f"{s} · {OMICS.get(r.omics_type, r.omics_type.lower())}"

df["label"] = df.apply(short, axis=1)
GROUPS = [("light", "Light"), ("non-light stress", "Non-light stress"), ("non-stress", "Non-stress (comparison)")]
TYPE_ORDER = ["sound", "approximate", "descriptive"]
TYPE_TEXT = {
    "sound": "Sound test (full table)",
    "approximate": "Approximate (significant-only table)",
    "descriptive": "Descriptive only",
}
N_HLI = int(df.hli_set_size.iloc[0])

# --- layout -----------------------------------------------------------------
ROW, GAP_GROUP, LABEL_W, BAR_W, RIGHT = 22, 30, 330, 260, 52
W = LABEL_W + BAR_W + RIGHT
parts, y = [], 8
for key, title in GROUPS:
    g = df[df.proposed_group == key].sort_values(["stress_type", "hli_measured"], ascending=[True, False])
    n_types = g.stress_type.nunique()
    parts.append(f'<text class="ig-group" x="0" y="{y + 14}">{html.escape(title)} '
                 f'<tspan class="ig-muted">· {len(g)} experiments</tspan></text>')
    y += 24
    for _, r in g.iterrows():
        # In a significant-only table, "in the table" means "significant", not
        # "measured" - so no hli count is drawn for those rows (whole genome assumed measured).
        approx = r.test_type == "approximate"
        w = BAR_W if approx else BAR_W * r.hli_measured / N_HLI
        cov = ("hli coverage: whole genome on the platform; the table lists significant genes only"
               if approx else f"hli genes measured: {r.hli_measured} of {N_HLI}|"
               f"Chaperones {r.chaperones_measured}/{r.chaperones_set_size}, "
               f"oxidative stress {r.oxidative_stress_measured}/{r.oxidative_stress_set_size}, "
               f"photosystem II {r.photosystem_II_measured}/{r.photosystem_II_set_size}")
        tip = (f"{r.experiment_name}|Stress type: {r.stress_type}|Data: {r.omics_type}|"
               f"Time points: {r.n_timepoints}|{TYPE_TEXT[r.test_type]}|{cov}")
        parts.append(
            f'<g class="ig-row" data-tip="{html.escape(tip)}">'
            f'<rect class="ig-hit" x="0" y="{y}" width="{W}" height="{ROW}"/>'
            f'<text class="ig-label" x="{LABEL_W - 10}" y="{y + 15}" text-anchor="end">{html.escape(r.label)}</text>'
            f'<rect class="ig-track" x="{LABEL_W}" y="{y + 5}" width="{BAR_W}" height="12" rx="4"/>'
            + (f'<rect class="ig-bar t-{r.test_type}" x="{LABEL_W}" y="{y + 5}" width="{max(w, 0):.1f}" height="12" rx="4"/>' if w > 0 else "")
            + f'<text class="ig-val" x="{LABEL_W + BAR_W + 6}" y="{y + 15}">{"genome" if approx else r.hli_measured}</text></g>')
        y += ROW
    y += GAP_GROUP - ROW + 14
H = y
axis = (f'<text class="ig-muted" x="{LABEL_W}" y="{H}" >0</text>'
        f'<text class="ig-muted" x="{LABEL_W + BAR_W}" y="{H}" text-anchor="end">{N_HLI} hli genes</text>')
svg = (f'<svg class="ig-chart" viewBox="0 0 {W} {H + 6}" role="img" '
       f'aria-label="hli genes measured in each MED4 experiment, by group and test type">'
       + "".join(parts) + axis + "</svg>")

# --- experiment and publication tables (verbose KG metadata) --------------------
from multiomics_explorer import list_experiments, list_publications  # noqa: E402

meta = {e["experiment_id"]: e for e in list_experiments(
    organism="MED4", experiment_ids=list(df.experiment_id), verbose=True, limit=None)["results"]}
assert set(meta) == set(df.experiment_id)
pubs = {p["doi"]: p for p in list_publications(
    publication_dois=sorted({m["publication_doi"] for m in meta.values()}), limit=None)["results"]}

def first_author(doi):
    p = pubs.get(doi, {})
    a = (p.get("authors") or ["?"])[0].split()[-1]
    return f"{a} {p.get('year', '')}".strip()

def cell(x):
    return html.escape(str(x)) if x not in (None, "", []) else "—"

exp_rows = []
for key, title in GROUPS:
    g = df[df.proposed_group == key].sort_values(["stress_type", "experiment_id"])
    exp_rows.append(f'<tr class="grp"><td colspan="7">{html.escape(title)}</td></tr>')
    for _, r in g.iterrows():
        m = meta[r.experiment_id]
        tps = ", ".join(t["timepoint"] for t in (m.get("timepoints") or [])) or "single"
        bg = ", ".join(m["background_factors"])
        cond = "; ".join(x for x in [m.get("light_condition"), m.get("light_intensity"),
                                     m.get("temperature")] if x)
        exp_rows.append(
            f"<tr><td>{cell(r.stress_type)}</td><td>{cell(m.get('treatment'))}</td><td>{cell(m.get('control'))}</td>"
            f"<td>{cell(bg)}<div class='ig-sub'>{cell(cond)}</div></td><td>{cell(tps)}</td>"
            f"<td>{OMICS.get(r.omics_type, r.omics_type.lower())} · {r.test_type}</td>"
            f"<td>{cell(first_author(m['publication_doi']))}</td></tr>")
exp_table = ("<table class='ig-t'><tr><th>Stress</th><th>Treatment</th><th>Compared against</th>"
             "<th>Background</th><th>Time points</th><th>Data · test</th><th>Study</th></tr>"
             + "".join(exp_rows) + "</table>")

used = df.merge(pd.DataFrame([{"experiment_id": k, "doi": v["publication_doi"]} for k, v in meta.items()]))
pub_rows = []
for doi, g in used.groupby("doi"):
    p = pubs.get(doi, {})
    groups = ", ".join(sorted(g.proposed_group.unique()))
    pub_rows.append((p.get("year", 0), f"<tr><td>{cell(first_author(doi))}</td><td>{cell(p.get('title'))}"
                     f"<div class='ig-sub'>{cell(p.get('journal'))} · <a href='https://doi.org/{doi}'>{doi}</a></div></td>"
                     f"<td>{len(g)}</td><td>{cell(groups)}</td></tr>"))
pub_table = ("<table class='ig-t'><tr><th>Study</th><th>Title</th><th>Experiments used</th><th>Group</th></tr>"
             + "".join(r for _, r in sorted(pub_rows)) + "</table>")

# Coverage of the comparison sets in full tables (significant-only tables: genome assumed).
cov_sets = [("hli", "hli"), ("chaperones", "Chaperones"), ("oxidative_stress", "Oxidative stress"),
            ("photosystem_II", "Photosystem II")]
full = df[df.test_type != "approximate"]
cov_rows = []
for key, title in GROUPS:
    g = full[full.proposed_group == key]
    if g.empty:
        continue
    cells = "".join(f"<td>{int(g[f'{c}_measured'].median())} / {int(g[f'{c}_set_size'].iloc[0])}"
                    f"<div class='ig-sub'>range {int(g[f'{c}_measured'].min())}–{int(g[f'{c}_measured'].max())}</div></td>"
                    for c, _ in cov_sets)
    cov_rows.append(f"<tr><td>{html.escape(title)}<div class='ig-sub'>{len(g)} full tables</div></td>{cells}</tr>")
cov_table = ("<table class='ig-t'><tr><th>Group</th>" + "".join(f"<th>{t}</th>" for _, t in cov_sets)
             + "</tr>" + "".join(cov_rows) + "</table>")

legend = "".join(f'<span class="ig-key"><i class="t-{t}"></i>{TYPE_TEXT[t]}</span>' for t in TYPE_ORDER)

counts = {k: int((df.proposed_group == k).sum()) for k, _ in GROUPS}
stress_types = df[df.proposed_group == "non-light stress"].stress_type.nunique()
prot_hl = df[df.experiment_name.str.contains("high light", case=False) & (df.omics_type == "PROTEOMICS")]
tiles = [
    (str(N_HLI), "hli genes in MED4", "all three ways of counting agree"),
    (str(len(df)), "usable experiments", f"{counts['light']} light · {counts['non-light stress']} stress · {counts['non-stress']} non-stress"),
    (str(stress_types), "non-light stress types", ", ".join(sorted(df[df.proposed_group == 'non-light stress'].stress_type.unique()))),
    (str(int(prot_hl.hli_measured.sum())), "hli proteins in high-vs-low light proteomics", "the only true excess-light test has no hli data"),
]
tiles_html = "".join(
    f'<div class="ig-tile"><div class="ig-num">{n}</div><div class="ig-cap">{html.escape(c)}</div>'
    f'<div class="ig-sub">{html.escape(s)}</div></div>' for n, c, s in tiles)

sets_html = "".join(
    f"<tr><td>{name}</td><td>{int(df[f'{col}_set_size'].iloc[0])}</td><td>{exp}</td></tr>"
    for name, col, exp in [
        ("hli (target)", "hli", "the genes being scored"),
        ("Chaperones", "chaperones", "general stress: up in most stresses"),
        ("Oxidative stress", "oxidative_stress", "general stress: up in many stresses"),
        ("Photosystem II", "photosystem_II", "tracks light; often down in nutrient stress"),
    ])

fragment = f"""{START}
<style>
.ig-tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:12px 0 18px}}
.ig-tile{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
.ig-num{{font-size:1.9rem;font-weight:650;line-height:1.1}}
.ig-cap{{font-weight:600;font-size:.9rem}} .ig-sub{{color:var(--muted);font-size:.8rem;margin-top:2px}}
.ig-wrap{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;position:relative}}
.ig-chart{{width:100%;height:auto;display:block;font:12px system-ui,-apple-system,"Segoe UI",sans-serif}}
.ig-group{{font-weight:650;font-size:13px;fill:var(--fg)}} .ig-muted{{fill:var(--muted);font-weight:400;font-size:11px}}
.ig-label{{fill:var(--fg)}} .ig-val{{fill:var(--muted);font-size:11px}}
.ig-track{{fill:var(--line);opacity:.45}} .ig-hit{{fill:transparent}} .ig-row:hover .ig-hit{{fill:var(--line);opacity:.35}}
.t-sound{{fill:#470f84;background:#470f84}} .t-approximate{{fill:#9e9ac8;background:#9e9ac8}}
.t-descriptive{{fill:transparent;stroke:#7b74b5;stroke-width:1.5;stroke-dasharray:3 2;background:transparent;outline:1.5px dashed #7b74b5;outline-offset:-1.5px}}
@media (prefers-color-scheme:dark){{.t-sound{{fill:#9e9ac8;background:#9e9ac8}} .t-approximate{{fill:#61409b;background:#61409b}}
.t-descriptive{{stroke:#7b74b5;outline-color:#7b74b5}}}}
.ig-legend{{display:flex;flex-wrap:wrap;gap:14px;font-size:.85rem;margin:0 0 8px}}
.ig-key i{{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}}
.ig-tip{{position:absolute;pointer-events:none;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:.8rem;box-shadow:0 4px 14px rgba(0,0,0,.15);max-width:340px;display:none;z-index:2}}
.ig-tip b{{display:block;margin-bottom:3px}}
details.ig-table{{margin-top:10px;font-size:.85rem}} details.ig-table summary{{cursor:pointer;padding:6px 0}}
.ig-t{{font-size:.82rem}} .ig-t tr.grp td{{font-weight:650;background:var(--bg)}} .ig-t a{{color:var(--accent)}}
</style>
<h2>What the KG holds (MED4)</h2>
<div class="ig-tiles">{tiles_html}</div>
<p><b>hli genes measured in each experiment.</b> Bar length = how many of the {N_HLI} hli genes the experiment measured; colour = how soundly it can be tested. Hover a row for details. In a full table a missing hli gene means "not measured", not "not changed". Tables that list only significant genes show a full bar marked "genome": the platform measured the whole genome, and the table cannot tell us more.</p>
<div class="ig-legend">{legend}</div>
<div class="ig-wrap" id="ig-wrap">{svg}<div class="ig-tip" id="ig-tip"></div></div>
<p class="sub" style="margin-top:8px">Left out: {len(excluded)} experiments — no stressed-vs-control comparison (vesicles, start-site mapping, RNA decay, annotation survey, day–night series, steady-state profiling), and all 8 proteomics experiments (dropped by decision; 4 of them measured no hli). In the darkness experiments the treatment is darkness, so they are read as "less light".</p>
<h3 style="font-size:1rem;margin:18px 0 6px">Gene sets</h3>
<table><tr><th>Set</th><th>MED4 genes</th><th>Role / expected result</th></tr>{sets_html}</table>
<h3 style="font-size:1rem;margin:18px 0 6px">Coverage of each gene set (full tables only)</h3>
<p class="sub">Median genes measured / set size, per experiment group. Significant-only tables are left out: there the whole genome was measured.</p>
{cov_table}
<details class="ig-table"><summary><b>Experiments: treatment, control and background</b> ({len(df)})</summary>{exp_table}</details>
<details class="ig-table"><summary><b>Publications</b> ({len(pub_rows)})</summary>{pub_table}</details>
<script>
(function(){{var w=document.getElementById('ig-wrap'),t=document.getElementById('ig-tip');
w.querySelectorAll('.ig-row').forEach(function(g){{
g.addEventListener('mousemove',function(e){{var p=g.getAttribute('data-tip').split('|');
t.innerHTML='<b>'+p[0]+'</b>'+p.slice(1).join('<br>');t.style.display='block';
var r=w.getBoundingClientRect(),x=e.clientX-r.left+14,y=e.clientY-r.top+14;
if(x+t.offsetWidth>r.width)x=e.clientX-r.left-t.offsetWidth-14;t.style.left=x+'px';t.style.top=y+'px';}});
g.addEventListener('mouseleave',function(){{t.style.display='none';}});}});}})();
</script>
{END}"""

page = OVERVIEW.read_text(encoding="utf-8")
if START in page:
    page = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda m: fragment, page, flags=re.S)
else:
    page = page.replace("<h2>Decisions so far</h2>", fragment + "\n\n<h2>Decisions so far</h2>")
OVERVIEW.write_text(page, encoding="utf-8")
print(f"rows={len(df)} excluded={len(excluded)} height={H}")
print(df.groupby(["proposed_group", "test_type"]).size().to_string())
