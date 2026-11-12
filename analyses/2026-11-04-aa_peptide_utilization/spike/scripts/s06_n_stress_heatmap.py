"""Spike: heatmap of per-timepoint log2FC (MED4 N-stress experiments) for the AA/peptide genes + reference N genes.
Reads data/med4_n_stress_de_long.csv. PNG+SVG (matplotlib) and an interactive HTML (hover per cell).
Run (repo root): PYTHONUTF8=1 uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s06_n_stress_heatmap.py
"""
import html
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, to_hex
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
DATA, REP, FIG = ROOT / "data", ROOT / "reports", ROOT / "figures"
FIG.mkdir(exist_ok=True)
CMAP = LinearSegmentedColormap.from_list("spock_diverging", ["#2a78d6", "#f0efec", "#eb6834"])
MISSING = "#a9a9a5"
LIM = 4.0

d = pd.read_csv(DATA / "med4_n_stress_de_long.csv", encoding="utf-8", keep_default_na=False)
d["log2fc"] = pd.to_numeric(d.log2fc, errors="coerce")
d["in_table"] = d.in_table.astype(str) == "True"

GROUPS = ["reference: N response", "uptake", "N-entry enzyme", "peptidase", "N-assimilation core"]
def group(r):
    if r.reference:
        return GROUPS[0]
    for g in GROUPS[1:]:
        if g in r.role:
            return g
    return "other"
genes = d.drop_duplicates("locus_tag")[["locus_tag", "gene_name", "reference", "role", "subrole"]].copy()
genes["group"] = genes.apply(group, axis=1)
genes["gi"] = genes.group.map(GROUPS.index)
genes = genes.sort_values(["gi", "subrole", "locus_tag"]).reset_index(drop=True)
genes["label"] = genes.apply(lambda r: f"{r.gene_name} ({r.locus_tag})" if r.gene_name else r.locus_tag, axis=1)

cols = (d.drop_duplicates(["exp_order", "experiment_label", "timepoint_order", "timepoint"])
        [["exp_order", "experiment_label", "experiment_id", "timepoint_order", "timepoint", "omics", "exp_table_scope"]]
        .sort_values(["exp_order", "timepoint_order"]).reset_index(drop=True))
cols["key"] = cols.experiment_id + "|" + cols.timepoint
d["key"] = d.experiment_id + "|" + d.timepoint
cell = d.set_index(["locus_tag", "key"])
M = np.full((len(genes), len(cols)), np.nan)
S = np.zeros_like(M, dtype=bool)
for i, lt in enumerate(genes.locus_tag):
    for j, k in enumerate(cols.key):
        r = cell.loc[(lt, k)]
        if r.in_table:
            M[i, j] = r.log2fc
            S[i, j] = str(r.expression_status).startswith("significant")

# ---------- static figure ----------
norm = TwoSlopeNorm(vmin=-LIM, vcenter=0, vmax=LIM)
h = 0.16 * len(genes) + 3.2
fig, ax = plt.subplots(figsize=(13, h))
ax.set_facecolor(MISSING)
Mc = np.ma.masked_invalid(np.clip(M, -LIM, LIM))
im = ax.pcolormesh(Mc, cmap=CMAP, norm=norm, edgecolors="#fcfcfb", linewidth=0.4)
yy, xx = np.nonzero(S)
ax.scatter(xx + 0.5, yy + 0.5, s=6, c="#1f2328", marker="o", linewidths=0)
ax.set_xlim(0, len(cols)); ax.set_ylim(len(genes), 0)
ax.set_yticks(np.arange(len(genes)) + 0.5, genes.label, fontsize=5.6)
ax.set_xticks(np.arange(len(cols)) + 0.5, cols.timepoint, fontsize=6.5, rotation=90)
ax.tick_params(length=0)
# experiment dividers + labels on top
starts = cols.groupby("exp_order").cumcount() == 0
for j in np.nonzero(starts.values)[0][1:]:
    ax.axvline(j, color="#1f2328", lw=1.0)
for eo, g in cols.groupby("exp_order"):
    ax.text(g.index.min() + 0.3, -0.8, g.experiment_label.iloc[0], rotation=60, ha="left", va="bottom",
            fontsize=6.5, color="#1f2328")
# group dividers
for gi, g in genes.groupby("gi"):
    if g.index.min() > 0:
        ax.axhline(g.index.min(), color="#1f2328", lw=1.0)
    ax.text(len(cols) + 0.4, g.index.min() + len(g) / 2, GROUPS[gi], rotation=270, va="center", ha="left",
            fontsize=7.5, color="#1f2328")
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.06, shrink=0.25, anchor=(0, 1))
cb.set_label(f"log2FC, treatment vs reference (clipped at ±{LIM:g})\n← lower in treatment · higher in treatment →", fontsize=7)
cb.ax.tick_params(labelsize=6)
ax.legend(handles=[Line2D([], [], marker="o", ls="", color="#1f2328", ms=3, label="significant (paper's own criterion)"),
                   Patch(facecolor=MISSING, label="not measured / not in table (ismej17 = top-50% table)")],
          loc="upper left", bbox_to_anchor=(1.07, 0.70), fontsize=6.5, frameon=False)
ax.set_title("MED4 amino-acid / peptide genes and reference N-response genes in KG nitrogen experiments (per timepoint)",
             fontsize=9, loc="left", pad=150)
for ext in ("png", "svg"):
    fig.savefig(FIG / f"med4_n_stress_heatmap.{ext}", dpi=300, bbox_inches="tight", facecolor="#fcfcfb")
plt.close(fig)

# ---------- interactive HTML ----------
def hexcol(v):
    return MISSING if np.isnan(v) else to_hex(CMAP(norm(np.clip(v, -LIM, LIM))))
head1 = "".join(f"<th colspan='{len(g)}' class='ex'>{html.escape(g.experiment_label.iloc[0])}</th>"
                for _, g in cols.groupby("exp_order"))
head2 = "".join(f"<th class='tp{' fst' if starts.iloc[j] else ''}'>{html.escape(t)}</th>" for j, t in enumerate(cols.timepoint))
body = []
for i, gr in genes.iterrows():
    if i == 0 or gr.gi != genes.gi.iloc[i - 1]:
        body.append(f"<tr class='grp'><td colspan='{len(cols) + 2}'>{html.escape(GROUPS[gr.gi])}</td></tr>")
    tds = []
    for j, k in enumerate(cols.key):
        r = cell.loc[(gr.locus_tag, k)]
        v = M[i, j]
        tip = (f"{gr.label} · {cols.experiment_label[j]} · {cols.timepoint[j]} · "
               + (f"log2FC {v:+.2f}, padj {r.padj or 'n/a'}, {r.expression_status}" if r.in_table else r.status))
        tds.append(f"<td class='c{' fst' if starts.iloc[j] else ''}{' sig' if S[i, j] else ''}' style='background:{hexcol(v)}' "
                   f"title='{html.escape(tip)}'></td>")
    body.append(f"<tr><th class='lab'>{html.escape(gr.label)}</th><td class='sub'>{html.escape(gr.subrole[:60])}</td>{''.join(tds)}</tr>")
grad = ",".join(to_hex(CMAP(x)) for x in np.linspace(0, 1, 9))
page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>MED4 amino-acid/peptide genes in KG nitrogen experiments (spike)</title>
<style>
body{{margin:0;padding:22px 28px;background:#fcfcfb;color:#1f2328;font:13px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}}
h1{{font-size:20px;margin:0 0 4px}} .sub0{{color:#59636e;margin:0 0 10px;max-width:1300px}}
table{{border-collapse:collapse}} th.ex{{font-size:11px;font-weight:600;text-align:left;border-left:2px solid #1f2328;padding:2px 4px;max-width:120px;vertical-align:bottom}}
th.tp{{font-size:10px;font-weight:400;writing-mode:vertical-rl;transform:rotate(180deg);padding:2px 0;height:70px}}
th.lab{{font-size:11px;font-weight:400;text-align:right;padding-right:6px;white-space:nowrap;font-family:ui-monospace,Consolas,monospace}}
td.sub{{font-size:10px;color:#59636e;white-space:nowrap;padding-right:8px;max-width:220px;overflow:hidden;text-overflow:ellipsis}}
td.c{{width:22px;height:14px;border:1px solid #fcfcfb;position:relative}} .fst{{border-left:2px solid #1f2328!important}}
td.sig::after{{content:"";position:absolute;left:50%;top:50%;width:5px;height:5px;margin:-2.5px;border-radius:50%;background:#1f2328}}
tr.grp td{{font-weight:700;padding:8px 0 2px;border-bottom:1px solid #d0d7de}}
.leg{{display:flex;gap:22px;align-items:center;margin:8px 0 14px;font-size:12px}} .bar{{width:180px;height:12px;background:linear-gradient(90deg,{grad})}}
.sw{{display:inline-block;width:14px;height:12px;vertical-align:-2px;background:{MISSING}}} .dot{{display:inline-block;width:6px;height:6px;border-radius:50%;background:#1f2328}}
</style></head><body>
<h1>MED4 amino-acid / peptide genes and reference N-response genes in KG nitrogen experiments</h1>
<p class="sub0">Spike draft. Rows: genes grouped by role (reference N-response genes first); a gene in several roles sits in the first matching group.
Columns: experiment × timepoint in time order; each experiment block is compared against its own reference
(Tolonen06: N-replete at matched time; ismej17: N-replete matched; 2025 lowN: same series at day 7 (axenic) or day 11 (coculture); 2025 coculture vs axenic: day 11 vs axenic day 7, day 18 vs axenic day 14).
Hover a cell for values. Significance is each paper's own criterion.</p>
<div class="leg"><span>−{LIM:g}</span><div class="bar"></div><span>+{LIM:g} log2FC (blue = lower, orange = higher in treatment; clipped)</span>
<span><span class="dot"></span> significant</span><span><span class="sw"></span> not measured / not in table (ismej17 lists only the top 50% of genes by expression)</span></div>
<table><thead><tr><th></th><th></th>{head1}</tr><tr><th></th><th></th>{head2}</tr></thead><tbody>{''.join(body)}</tbody></table>
<p class="sub0">Source: data/med4_n_stress_de_long.csv ({len(d)} rows).</p></body></html>"""
(REP / "med4_n_stress_heatmap.html").write_text(page, encoding="utf-8")
print("genes", len(genes), "cols", len(cols), "sig cells", int(S.sum()), "missing cells", int(np.isnan(M).sum()))
print(genes.group.value_counts().to_string())
