"""Build a 1920x1080 HTML figure: MED4 amino-acid-related genes x expression experiments.
Input:  data/gene_response_profile_raw.json (MCP gene_response_profile, KG 0.1.0-alpha.9)
Output: ../../slides/fig_med4_expression.html (render to PNG with headless Edge)
Colour: orange = up, blue = down (template convention); intensity = largest |log2FC| (capped at 4).
"""
import json, pathlib, html

here = pathlib.Path(__file__).resolve().parents[1]
root = here.parents[1]
d = json.load(open(here / "data/gene_response_profile_raw.json", encoding="utf-8"))
genes = {r["locus_tag"]: r for r in d["results"]}

COLS = [  # (group, label, key substring)
    ("Short-term N deprivation", "Tolonen 2006<br><small>0–48 h</small>", "nitrogen_deprivation_med4"),
    ("Short-term N deprivation", "Read 2017<br><small>3–24 h</small>", "ismej.2017.88"),
    ("Long-term N starvation (2025)", "RNA<br><small>axenic</small>", "rnaseq_axenic"),
    ("Long-term N starvation (2025)", "RNA<br><small>coculture</small>", "rnaseq_coculture"),
    ("Long-term N starvation (2025)", "Protein<br><small>axenic</small>", "proteomics_axenic"),
    ("Long-term N starvation (2025)", "Protein<br><small>coculture</small>", "proteomics_coculture"),
    ("Other N source", "Urea<br><small>Tolonen</small>", "growth_on_urea"),
    ("Other N source", "Cyanate<br><small>Tolonen</small>", "growth_on_cyanate"),
    ("With Alteromonas", "2016<br><small>coculture</small>", "ismej.2016.70_coculture"),
    ("With Alteromonas", "2025<br><small>coculture</small>", "690089_coculture"),
]
ROWS = [
    ("Nitrogen controls", [("PMM0920", "glnA", "glutamine synthetase"), ("PMM0970", "urtA", "urea transporter"), ("PMM0963", "ureC", "urease")]),
    ("Amino-acid / peptide uptake", [("PMM0628", "gltS", "glutamate symporter (only AA uptake candidate)"), ("PMM1049", "dppA", "peptide-binding protein")]),
    ("Breakdown-only enzyme", [("PMM0821", "ansA", "asparaginase")]),
    ("Shared enzymes (not counted in breakdown)", [("PMM0878", "ilvE", "branched-chain aminotransferase"), ("PMM0186", "hisC", "histidinol-P aminotransferase"),
        ("PMM0674", "aspC", "aspartate aminotransferase"), ("PMM0919", "spt", "Ala/Gly aminotransferase"), ("PMM0908", "ilvA", "Thr dehydratase"),
        ("PMM1512", "glsF", "Fd-GOGAT")]),
    ("Other", [("PMM1084", "cadA", "Lys decarboxylase"), ("PMM1703", "—", "D-amino-acid dehydrogenase (broad)")]),
]

def cell(lt, key):
    rs = genes[lt]["response_summary"]
    e = next((k for k in rs if key in k), None)
    if e is None:
        return "<td class='na'>–</td>"
    s = rs[e]; u, dn, t = s["timepoints_up"], s["timepoints_down"], s["timepoints_tested"]
    if not u and not dn:
        return f"<td class='ns' title='not significant, {t} timepoint(s)'>ns</td>"
    up = u >= dn
    fc = s["up_max_log2fc"] if up else s["down_max_log2fc"]
    a = min(abs(fc), 4) / 4
    col = (217, 113, 28) if up else (47, 111, 181)
    bg = f"rgba({col[0]},{col[1]},{col[2]},{0.18 + 0.82 * a:.2f})"
    fg = "#fff" if a > 0.45 else "#1f2328"
    mix = " mixed" if u and dn else ""
    return (f"<td style='background:{bg};color:{fg}' title='{u} up, {dn} down of {t} timepoints{mix}'>"
            f"<b>{fc:+.1f}</b><small>{u + dn}/{t}</small></td>")

head1, head2, prev = [], [], None
for g, lab, _ in COLS:
    if g != prev:
        head1.append([g, 1]); prev = g
    else:
        head1[-1][1] += 1
    head2.append(f"<th>{lab}</th>")
h1 = "".join(f"<th colspan='{n}' class='grp'>{html.escape(g)}</th>" for g, n in head1)
body = []
for grp, rows in ROWS:
    body.append(f"<tr class='sec'><td colspan='{len(COLS) + 1}'>{html.escape(grp)}</td></tr>")
    for lt, gn, prod in rows:
        cells = "".join(cell(lt, k) for _, _, k in COLS)
        body.append(f"<tr><td class='gene'><b>{gn}</b> <span class='lt'>{lt}</span><small>{html.escape(prod)}</small></td>{cells}</tr>")

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="description" content="MED4 amino-acid-related genes across nitrogen and coculture expression experiments in the KG (orange up, blue down).">
<title>MED4 expression of amino-acid-related genes</title>
<style>
:root{{--ink:#1f2328;--muted:#59636e;--line:#d0d7de;--bg:#fcfcfb;--pro:#1f8a4c}}
*{{box-sizing:border-box}} html,body{{margin:0;background:#e9eaec}}
.slide{{width:1920px;height:1080px;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;padding:34px 56px 22px;display:grid;grid-template-rows:auto 1fr auto;gap:14px;overflow:hidden}}
h1{{margin:0;font-size:38px}} h1 i{{font-style:italic}} .sub{{margin:6px 0 0;font-size:20px;color:var(--muted)}}
.wrap{{display:grid;grid-template-columns:1fr 360px;gap:22px;min-height:0}}
table{{border-collapse:separate;border-spacing:3px;width:100%;font-size:16px}}
th{{font-size:15px;font-weight:600;color:var(--ink);padding:4px 2px;vertical-align:bottom}} th small{{color:var(--muted);font-weight:400}}
th.grp{{font-size:14px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);border-bottom:2px solid var(--line)}}
td{{text-align:center;height:43px;border-radius:5px;font-size:17px;line-height:1.05}} td small{{display:block;font-size:11px;opacity:.85}}
td.ns{{background:#f1f2f4;color:#8c939b;font-size:14px}} td.na{{background:transparent;color:#c4c8cd}}
td.gene{{text-align:left;background:transparent;width:330px;padding-left:4px}} td.gene small{{display:block;font-size:13px;color:var(--muted)}}
.lt{{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:var(--muted)}}
tr.sec td{{height:24px;text-align:left;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--pro);padding:6px 4px 0}}
.side{{display:flex;flex-direction:column;gap:12px}}
.card{{background:#f3f4f6;border-radius:12px;padding:14px 18px;font-size:17px;line-height:1.35}}
.card b.h{{display:block;font-size:19px;margin-bottom:4px}}
.key{{display:flex;align-items:center;gap:8px;font-size:15px;margin-top:6px}}
.sw{{width:70px;height:16px;border-radius:4px}}
.foot{{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:6px}}
</style></head><body><div class="slide">
<div><h1>What does <i>Prochlorococcus</i> MED4 switch on when nitrogen is short?</h1>
<p class="sub">Amino-acid-related genes across the 10 MED4 nitrogen and coculture experiments in our database · largest log₂ fold change, significant / tested timepoints</p></div>
<div class="wrap"><div><table><tr><th></th>{h1}</tr><tr><th></th>{''.join(head2)}</tr>{''.join(body)}</table></div>
<div class="side">
<div class="card"><b class="h">How to read it</b>Each cell = one gene in one experiment.
<div class="key"><span class="sw" style="background:linear-gradient(90deg,rgba(217,113,28,.25),rgb(217,113,28))"></span>up (log₂FC 0 → 4+)</div>
<div class="key"><span class="sw" style="background:linear-gradient(90deg,rgba(47,111,181,.25),rgb(47,111,181))"></span>down</div>
<div class="key"><span class="sw" style="background:#f1f2f4"></span>ns = not significant</div></div>
<div class="card"><b class="h">Short-term N deprivation</b>The nitrogen alarm fires (glnA, urtA up), but <b>no amino-acid gene responds</b>, not even gltS or asparaginase.</div>
<div class="card"><b class="h">Long-term starvation</b>Peptide-binding <b>dppA</b>, <b>ilvE</b> and <b>urease</b> rise: consistent with recycling the cell's own proteins and/or taking up <b>peptides</b>.</div>
<div class="card"><b class="h">Caveats</b>2025 contrasts are vs each culture's own exponential sample (starvation + aging). Extreme 2016 coculture values not yet checked. ns ≠ not expressed.</div>
</div></div>
<div class="foot">Data: KG 0.1.0-alpha.9 (Tolonen et al. 2006; Read et al. 2017; Aharonovich &amp; Sher 2016; Weissberg, Aharonovich &amp; Sher 2025). Exploration, not yet independently reviewed. Source table: spike/med4_expression/data/med4_aa_gene_responses.csv</div>
</div></body></html>"""
out = root / "slides/fig_med4_expression.html"
out.write_text(page, encoding="utf-8")
print("wrote", out)
