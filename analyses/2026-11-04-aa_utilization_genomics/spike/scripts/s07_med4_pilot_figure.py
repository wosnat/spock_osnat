"""MED4 pilot: dedicated-step status per amino acid, from the draft KO catalogue.

Reads spike/data/med4_aa_n_release.csv (catalogue x MED4 genes). Applies the pilot
reclassifications below in code, then writes the status table, a figure (PNG + SVG)
and a self-contained HTML page.

Run: uv run python analyses/2026-11-04-aa_utilization_genomics/spike/scripts/s07_med4_pilot_figure.py
"""
import html
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG, REP = ROOT / "data", ROOT / "figures", ROOT / "reports"
FIG.mkdir(exist_ok=True)
REP.mkdir(exist_ok=True)

AAS = ["Ala", "Arg", "Asn", "Asp", "Cys", "Glu", "Gln", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe",
       "Pro", "Ser", "Thr", "Trp", "Tyr", "Val"]
BROAD = "broad / D-amino-acid"

C_COMPLETE = "dedicated step found (pathway complete)"
C_PARTIAL = "dedicated step found (pathway partial)"
C_SHARED = "shared enzymes only (not counted)"
C_FLAG = "flagged: KO/product mismatch"
C_NONE = "nothing found"
PRIORITY = [C_COMPLETE, C_PARTIAL, C_SHARED, C_FLAG, C_NONE]

# Pilot reclassifications (from the coordinator, applied in code)
SHARED_OVERRIDE = {"K01428": "yes", "K01429": "yes", "K01430": "yes"}  # urease counts as shared (urea use)
BROAD_KOS = {"K00273"}                                                 # own row, never credited to an AA
FLAG_KO_GENE = {("K00639", "PMM1468")}                                # kbl KO on bioF gene
PARTIAL_KOS = {"K01582"}                                               # cadA: dedicated, N not freed here

# Palette: dataviz categorical slots 7 (violet), 3 (aqua), 4 (yellow), validated light all-pairs
# (contrast WARN for aqua/yellow -> every mark is direct-labelled and a table follows).
# Grey is a deliberate neutral for "not counted"; shape carries identity as well.
STYLE = {
    C_COMPLETE: dict(color="#6250d6", marker="o", fill=True),
    C_PARTIAL: dict(color="#1baf7a", marker="D", fill=True),
    C_SHARED: dict(color="#8f8e89", marker="s", fill=True),
    C_FLAG: dict(color="#eda100", marker="^", fill=True),
    C_NONE: dict(color="#8f8e89", marker="o", fill=False),
}
INK, INK2, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"


def classify(r):
    if r.ko in BROAD_KOS:
        return C_COMPLETE if r.shared == "no" else C_SHARED
    if (r.ko, r.locus_tag) in FLAG_KO_GENE:
        return C_FLAG
    if r.shared == "yes":
        return C_SHARED
    if r.ko in PARTIAL_KOS:
        return C_PARTIAL
    if r["mode"] in ("release_NH4", "transfer_transamination"):
        return C_COMPLETE
    return C_PARTIAL  # dedicated, but the step does not itself free the N


def build_items():
    nr = pd.read_csv(DATA / "med4_aa_n_release.csv", encoding="utf-8")
    hits = nr[nr.med4_gene_found].copy()
    hits["shared"] = hits.apply(lambda r: SHARED_OVERRIDE.get(r.ko, r.shared_interpretation), axis=1)
    hits["category"] = hits.apply(classify, axis=1)
    items = []
    for r in hits.itertuples():
        if r.amino_acid == "REF":
            continue  # glnA validation probe, not an amino-acid step
        rows = [BROAD] if r.ko in BROAD_KOS else r.amino_acid.split(";")
        for aa in rows:
            if aa == "ALL" and r.ko not in BROAD_KOS:
                aa = BROAD
            gname = r.gene_name if isinstance(r.gene_name, str) else "unnamed"
            items.append(dict(row=aa, ko=r.ko, label=r.label, gene=gname, locus_tag=r.locus_tag,
                              mode=r.mode, shared=r.shared, category=r.category,
                              text=f"{gname} ({r.locus_tag})"))
    return pd.DataFrame(items)


def status_table(items):
    out = []
    for aa in AAS + [BROAD]:
        it = items[items.row == aa] if len(items) else items
        cats = set(it.category) if len(it) else set()
        cat = next((c for c in PRIORITY if c in cats), C_NONE)
        def genes(c):
            s = it[it.category == c]
            return "; ".join(f"{r.ko}:{r.locus_tag}({r.gene})" for r in s.itertuples())
        out.append({
            "amino_acid": aa,
            "category": cat,
            "credited": "no" if aa == BROAD else ("yes" if cat in (C_COMPLETE, C_PARTIAL) else "no"),
            "dedicated_complete_genes": genes(C_COMPLETE),
            "dedicated_partial_genes": genes(C_PARTIAL),
            "shared_only_genes": genes(C_SHARED),
            "flagged_genes": genes(C_FLAG),
        })
    return pd.DataFrame(out)


def save_figure(fig, stem):
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight", facecolor=SURFACE)
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", facecolor=SURFACE)


def draw(items, status):
    rows = AAS + [BROAD]
    fig, ax = plt.subplots(figsize=(13, 9.2))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    step = 2.6  # x units per item (dot + label)
    for i, aa in enumerate(rows):
        y = len(rows) - 1 - i + (0 if aa != BROAD else -0.6)
        it = items[items.row == aa].copy() if len(items) else items
        if len(it):
            it["p"] = it.category.map(PRIORITY.index)
            it = it.sort_values(["p", "locus_tag"])
        if not len(it):
            st = STYLE[C_NONE]
            ax.plot(0, y, marker=st["marker"], ms=8, mfc="none", mec=st["color"], mew=1.5, ls="none")
            ax.text(0.25, y, "nothing found", va="center", ha="left", fontsize=8.5, color=INK2)
        for j, r in enumerate(it.itertuples()):
            st = STYLE[r.category]
            x = j * step
            ax.plot(x, y, marker=st["marker"], ms=8, mfc=st["color"] if st["fill"] else "none",
                    mec=SURFACE if st["fill"] else st["color"], mew=1.0, ls="none")
            ax.text(x + 0.25, y, r.text, va="center", ha="left", fontsize=8.5, color=INK)
        cat = status.loc[status.amino_acid == aa, "category"].iloc[0]
        if aa == BROAD:
            ax.axhline(y + 0.8, color="#d6d5d0", lw=0.8)
    ylabels = [(len(rows) - 1 - i + (0 if aa != BROAD else -0.6), aa) for i, aa in enumerate(rows)]
    ax.set_yticks([p for p, _ in ylabels])
    ax.set_yticklabels([l for _, l in ylabels], fontsize=10, color=INK)
    ax.set_xticks([])
    ax.set_xlim(-0.6, 5 * step + 1.5)
    ax.set_ylim(-1.3, len(rows) - 0.4)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#d6d5d0")
    ax.tick_params(axis="y", length=0)
    handles = []
    for c in PRIORITY:
        st = STYLE[c]
        handles.append(Line2D([0], [0], marker=st["marker"], ls="none", ms=8,
                              mfc=st["color"] if st["fill"] else "none",
                              mec=st["color"] if not st["fill"] else SURFACE, label=c))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.45, 1.075), ncol=3, frameon=False,
              fontsize=9, labelcolor=INK)
    fig.suptitle("MED4 pilot — draft catalogue, not approved", x=0.06, y=0.995, ha="left",
                 fontsize=14, color=INK, fontweight="bold")
    caption = ("Each mark is one MED4 gene annotated to a catalogued KEGG KO for that amino acid's nitrogen-removing "
               "or breakdown steps (draft catalogue, not approved; KG 0.1.0-alpha.9). Only dedicated (breakdown-only) "
               "steps count; enzymes shared with biosynthesis or central metabolism, including urease, are shown grey "
               "and not counted. \"Nothing found\" means no gene in this genome is annotated to any catalogued KO "
               "for that amino acid. The broad / D-amino-acid row (K00273) is never credited to an amino acid. "
               "Ile, Leu and Val share one branched-chain aminotransferase entry. Labels: gene (locus tag).")
    fig.text(0.06, -0.02, caption, ha="left", va="top", fontsize=8.5, color=INK2, wrap=True)
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.04)
    return fig


def write_html(status, svg_text):
    cols = ["amino_acid", "category", "credited", "dedicated_complete_genes", "dedicated_partial_genes",
            "shared_only_genes", "flagged_genes"]
    head = "".join(f"<th onclick=\"sortT({i})\">{html.escape(c)}</th>" for i, c in enumerate(cols))
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(r[c]))}</td>" for c in cols) + "</tr>"
                   for _, r in status.iterrows())
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>MED4 pilot: amino-acid dedicated-step status (draft)</title>
<meta name="description" content="Throwaway MED4 spike: which catalogued amino-acid breakdown enzymes MED4 carries, scored on dedicated steps only; draft catalogue, not approved.">
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;background:#fcfcfb;color:#0b0b0b;max-width:1200px;margin:2rem auto;padding:0 1rem;}}
p.note{{color:#52514e;font-size:0.95rem}} svg{{max-width:100%;height:auto}}
table{{border-collapse:collapse;font-size:0.85rem;width:100%}} th,td{{border-bottom:1px solid #e3e2de;padding:4px 6px;text-align:left;vertical-align:top}}
th{{cursor:pointer;background:#f0efec}}
</style></head><body>
<h1>MED4 pilot &mdash; draft catalogue, not approved</h1>
<p class="note">Throwaway spike (one strain). The KO catalogue is a draft drafted from standard biochemistry and not yet approved.
Only dedicated (breakdown-only) steps are credited; shared enzymes (including urease) are shown but not counted.
&ldquo;Nothing found&rdquo; means no gene in this genome is annotated to a catalogued KO. Source: spike/data/med4_aa_n_release.csv;
script: spike/scripts/s07_med4_pilot_figure.py.</p>
{svg_text}
<h2>Per-amino-acid status</h2>
<p class="note">Click a column header to sort. Genes given as KO:locus_tag(gene).</p>
<table id="t"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
<script>
function sortT(n){{const t=document.getElementById('t');const rows=[...t.tBodies[0].rows];
const asc=t.dataset.col==n&&t.dataset.dir!='asc';t.dataset.col=n;t.dataset.dir=asc?'asc':'desc';
rows.sort((a,b)=>{{const x=a.cells[n].textContent,y=b.cells[n].textContent;return asc?x.localeCompare(y):y.localeCompare(x)}});
rows.forEach(r=>t.tBodies[0].appendChild(r));}}
</script></body></html>"""
    (REP / "med4_pilot_summary.html").write_text(page, encoding="utf-8")


def main():
    items = build_items()
    status = status_table(items)
    status.to_csv(DATA / "med4_pilot_pathway_status.csv", index=False, encoding="utf-8")
    fig = draw(items, status)
    save_figure(fig, FIG / "med4_pilot_summary")
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", facecolor=SURFACE)
    svg = buf.getvalue()
    svg = svg[svg.find("<svg"):]
    write_html(status, svg)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 120)
    print(status.to_markdown(index=False))
    print("items:", len(items))


if __name__ == "__main__":
    main()
