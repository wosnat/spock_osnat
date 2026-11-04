"""MED4 pilot: what was searched and what was found (enzyme-level preview).

Reads spike/data/med4_n_release_catalogue.csv (every catalogued KO) and
spike/data/med4_aa_n_release.csv (MED4 hits). Applies the s07 overrides in code.
Writes the amino acid x KO matrix CSV, a 3-panel figure (PNG + SVG) and an HTML page
with hover tooltips on tiles and a sortable table.

Run: uv run python analyses/2026-11-04-aa_utilization_genomics/spike/scripts/s08_med4_pilot_matrix.py
"""
import html
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from matplotlib.lines import Line2D
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG, REP = ROOT / "data", ROOT / "figures", ROOT / "reports"
FIG.mkdir(exist_ok=True)
REP.mkdir(exist_ok=True)

AAS = ["Ala", "Arg", "Asn", "Asp", "Cys", "Glu", "Gln", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe",
       "Pro", "Ser", "Thr", "Trp", "Tyr", "Val"]
BROAD = "broad / D-amino-acid"

# --- overrides (same as s07) ---
SHARED_OVERRIDE = {"K01428": ("yes", "urease: urea use (override)"),
                   "K01429": ("yes", "urease: urea use (override)"),
                   "K01430": ("yes", "urease: urea use (override)"),
                   "K01582": ("yes", "decarboxylase to polyamine, same class as speA (override)")}
BROAD_KOS = {"K00273"}            # never credited; plus every catalogue row with amino_acid == ALL
FLAG_KO_GENE = {("K00639", "PMM1468")}
VIA_UREA = {"K01476", "K01480", "K01428", "K01429", "K01430"}

# short enzyme names for tiles (display labels only)
SHORT = {
    "K00259": "AlaDH", "K00285": "D-AA DH", "K14260": "Ala AT", "K00814": "Ala AT (GPT)", "K00835": "avtA",
    "K01476": "arginase", "K01478": "Arg deiminase", "K00611": "OTC", "K00926": "carbamate kin.",
    "K01585": "Arg decarbox.", "K01480": "agmatinase", "K12252": "aruH", "K00819": "Orn AT",
    "K01428": "urease α", "K01429": "urease β", "K01430": "urease γ",
    "K01424": "asparaginase", "K13051": "isoAsp-asparag.", "K01744": "aspartase", "K00278": "Asp oxidase",
    "K00812": "AspAT (aspB)", "K00813": "AspAT (aspC)", "K11358": "AspAT (yhdR)", "K14454": "GOT1",
    "K14455": "GOT2", "K01760": "metC", "K05396": "D-Cys desulfh.", "K17217": "Cys γ-lyase",
    "K01738": "cysK", "K00261": "GDH NAD(P)", "K00262": "GDH NADP", "K15371": "GDH NAD",
    "K01580": "Glu decarbox.", "K01425": "glutaminase", "K00265": "GOGAT large", "K00266": "GOGAT small",
    "K00284": "Fd-GOGAT", "K00281": "gcvP", "K00605": "gcvT", "K02437": "gcvH", "K03153": "Gly oxidase",
    "K00830": "AGXT", "K01745": "hutH", "K01712": "hutU", "K01468": "hutI", "K01479": "hutG",
    "K00817": "hisC", "K00826": "BCAT (ilvE)", "K00263": "LeuDH", "K03918": "Lys AT", "K01582": "Lys decarbox.",
    "K01761": "Met γ-lyase", "K00832": "tyrB", "K00838": "ARO8", "K10775": "PAL", "K13064": "PTAL",
    "K00270": "PheDH", "K00815": "Tyr AT", "K00318": "PRODH", "K13821": "putA", "K00294": "P5C DH",
    "K01752": "Ser dehydratase", "K01753": "D-Ser dehydr.", "K01754": "Thr dehydratase", "K17989": "Ser/Thr dehydr.",
    "K01620": "Thr aldolase", "K00060": "Thr DH", "K00639": "kbl", "K01667": "tryptophanase",
    "K03334": "L-AA oxidase", "K00273": "D-AA oxidase", "K14267": "dapC", "K10907": "AT (K10907)",
    "K00837": "AT (ALD1)",
}
MODE_ORDER = ["NH4+", "via urea", "transfer", "other"]
MODE_GLYPH = {"NH4+": "NH₄⁺", "via urea": "urea", "transfer": "TA", "other": "oth"}

# palette (s07): violet dedicated, grey shared, yellow flagged, dark ink broad
VIOLET, GREY, YELLOW, INKD = "#6250d6", "#8f8e89", "#eda100", "#52514e"
INK, INK2, SURFACE, RULE = "#0b0b0b", "#52514e", "#fcfcfb", "#d6d5d0"
C_DED, C_SHARED, C_NONE = "dedicated enzyme found", "shared enzymes only (not counted)", "nothing found"
CAT_COLOR = {C_DED: VIOLET, C_SHARED: GREY, C_NONE: SURFACE}


def mode_of(r):
    if r.ko in VIA_UREA:
        return "via urea"
    return {"release_NH4": "NH4+", "transfer_transamination": "transfer"}.get(r.mode, "other")


def build_matrix():
    cat = pd.read_csv(DATA / "med4_n_release_catalogue.csv", encoding="utf-8")
    hits = pd.read_csv(DATA / "med4_aa_n_release.csv", encoding="utf-8")
    hits = hits[hits.med4_gene_found]
    cat = cat[cat.amino_acid != "REF"]  # glnA validation probe excluded
    rows = []
    for r in cat.itertuples():
        aas = [BROAD] if (r.amino_acid == "ALL" or r.ko in BROAD_KOS) else r.amino_acid.split(";")
        h = hits[(hits.ko == r.ko)]
        loci = sorted(h.locus_tag.unique())
        genes = [f"{lt}({g if isinstance(g, str) else 'unnamed'})" for lt, g in zip(h.locus_tag, h.gene_name)]
        flagged = any((r.ko, lt) in FLAG_KO_GENE for lt in loci)
        shared, reason = SHARED_OVERRIDE.get(r.ko, (r.shared_interpretation,
                                                     "draft catalogue: " + ("shared with biosynthesis/central metabolism"
                                                                            if r.shared_interpretation == "yes"
                                                                            else "breakdown-only")))
        for aa in aas:
            if aa == BROAD:
                cls = "broad"
            elif flagged:
                cls = "flagged"
            else:
                cls = "dedicated" if shared == "no" else "shared"
            rows.append({"amino_acid": aa, "ko": r.ko, "enzyme": SHORT.get(r.ko, r.label), "label": r.label,
                         "ec": r.ec, "mode": mode_of(r), "shared": shared, "shared_reason": reason,
                         "class": cls, "in_kg": bool(r.ko_in_kg), "found": len(loci) > 0,
                         "locus_tags": ";".join(loci), "genes": "; ".join(genes), "kg_ko_name": r.kg_ko_name,
                         "note": r.note})
    m = pd.DataFrame(rows)
    m["mode_rank"] = m["mode"].map(MODE_ORDER.index)
    return m.sort_values(["amino_acid", "mode_rank", "ko"]).drop(columns="mode_rank")


def row_category(m, aa):
    s = m[m.amino_acid == aa]
    if ((s["class"] == "dedicated") & s.found).any():
        return C_DED
    if ((s["class"] == "shared") & s.found).any():
        return C_SHARED
    return C_NONE


def save_figure(fig, stem):
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight", facecolor=SURFACE)
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", facecolor=SURFACE)


def draw(m, cats, counts_aa, counts_enz):
    order = sorted(AAS, key=lambda a: ([C_DED, C_SHARED, C_NONE].index(cats[a]), AAS.index(a)))
    rows = order + [BROAD]
    maxn = max(len(m[m.amino_acid == a]) for a in rows)
    TW, TH, GAP = 1.0, 0.56, 0.12
    fig = plt.figure(figsize=(17, 17.5))
    fig.patch.set_facecolor(SURFACE)
    gs = fig.add_gridspec(3, 2, height_ratios=[0.9, 14, 2.6], width_ratios=[1, 1], hspace=0.12, wspace=0.35)

    # --- A: status strip ---
    axA = fig.add_subplot(gs[0, :])
    for i, a in enumerate(order):
        c = cats[a]
        axA.add_patch(Rectangle((i * 1.05, 0), 1.0, 1.0, facecolor=CAT_COLOR[c],
                                edgecolor=GREY if c == C_NONE else SURFACE, lw=1.2))
        axA.text(i * 1.05 + 0.5, 0.5, a, ha="center", va="center", fontsize=10,
                 color="white" if c == C_DED else INK, fontweight="bold" if c == C_DED else "normal")
        if (m[(m.amino_acid == a)]["class"] == "flagged").any():
            axA.add_patch(Polygon([[i * 1.05 + 0.72, 0.98], [i * 1.05 + 0.98, 0.98], [i * 1.05 + 0.98, 0.72]],
                                  closed=True, facecolor=YELLOW, edgecolor=SURFACE, lw=0.8))
    axA.set_xlim(-0.1, 20 * 1.05)
    axA.set_ylim(-0.05, 1.05)
    axA.axis("off")
    axA.set_title("A  Status per amino acid (enzyme-level)", loc="left", fontsize=11, color=INK, pad=6)

    # --- B: enzyme matrix ---
    axB = fig.add_subplot(gs[1, :])
    tiles = {}
    for i, a in enumerate(rows):
        y = -(i * 1.0) - (0.6 if a == BROAD else 0)
        s = m[m.amino_acid == a]
        axB.text(-0.25, y, a, ha="right", va="center", fontsize=10, color=INK)
        prev_mode = None
        x = 0.0
        for r in s.itertuples():
            if prev_mode is not None and r.mode != prev_mode:
                x += 0.35  # gap between mode groups
            prev_mode = r.mode
            col = {"dedicated": VIOLET, "shared": GREY, "flagged": YELLOW, "broad": INKD}[m.loc[r.Index, "class"]]
            filled = bool(r.found)
            p = Rectangle((x, y - TH / 2), TW, TH, facecolor=col if filled else SURFACE,
                          edgecolor=col, lw=1.3, linestyle="-" if r.in_kg else (0, (2, 1.5)))
            gid = f"tile{r.Index}"
            p.set_gid(gid)
            axB.add_patch(p)
            tiles[gid] = int(r.Index)
            txtcol = "white" if (filled and col in (VIOLET, INKD)) else INK
            axB.text(x + TW / 2, y + 0.06, r.enzyme, ha="center", va="center", fontsize=6.3, color=txtcol)
            axB.text(x + TW - 0.04, y - TH / 2 + 0.06, MODE_GLYPH[r.mode], ha="right", va="bottom",
                     fontsize=5.0, color=txtcol)
            below = r.locus_tags.replace(";", ", ") if filled else ("not in KG" if not r.in_kg else "")
            if below:
                axB.text(x + TW / 2, y - TH / 2 - 0.05, below, ha="center", va="top", fontsize=5.6,
                         color=INK if filled else INK2, style="normal" if filled else "italic")
            x += TW + GAP
        if a == BROAD:
            axB.axhline(y + 0.8, color=RULE, lw=0.8)
    axB.set_xlim(-2.4, maxn * (TW + GAP) + 3 * 0.35 + 0.2)
    axB.set_ylim(-(len(rows) - 1) - 2.6, 0.7)
    axB.axis("off")
    axB.set_title("B  Catalogued enzymes per amino acid: filled = found in MED4, hollow = searched, no gene annotated",
                  loc="left", fontsize=11, color=INK, pad=6)
    handles = [
        Rectangle((0, 0), 1, 1, facecolor=VIOLET, edgecolor=VIOLET, label="dedicated, found"),
        Rectangle((0, 0), 1, 1, facecolor=SURFACE, edgecolor=VIOLET, lw=1.3, label="dedicated, searched, not found"),
        Rectangle((0, 0), 1, 1, facecolor=GREY, edgecolor=GREY, label="shared, found (not counted)"),
        Rectangle((0, 0), 1, 1, facecolor=SURFACE, edgecolor=GREY, lw=1.3, label="shared, searched, not found"),
        Rectangle((0, 0), 1, 1, facecolor=YELLOW, edgecolor=YELLOW, label="flagged: KO/product mismatch"),
        Rectangle((0, 0), 1, 1, facecolor=INKD, edgecolor=INKD, label="broad, never credited"),
        Rectangle((0, 0), 1, 1, facecolor=SURFACE, edgecolor=INK2, lw=1.3, linestyle=(0, (2, 1.5)),
                  label="dashed = KO not in KG (unchecked vs KEGG)"),
        Line2D([0], [0], ls="none", label="corner text: NH₄⁺ / urea / TA (transfer) / oth = N-mode"),
    ]
    axB.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 0.0), fontsize=8, frameon=False,
               labelcolor=INK, ncol=4)

    # --- C: counts ---
    axC1 = fig.add_subplot(gs[2, 0])
    labs = [C_DED, C_SHARED, C_NONE]
    vals = [counts_aa[c] for c in labs]
    axC1.barh(range(3), vals, color=[VIOLET, GREY, SURFACE], edgecolor=[VIOLET, GREY, GREY], height=0.6, lw=1.2)
    for i, v in enumerate(vals):
        axC1.text(v + 0.2, i, str(v), va="center", fontsize=9, color=INK)
    axC1.set_yticks(range(3))
    axC1.set_yticklabels(labs, fontsize=9, color=INK)
    axC1.invert_yaxis()
    axC1.set_xlim(0, 21)
    axC1.set_title("C  Amino acids per category (n = 20)", loc="left", fontsize=11, color=INK)
    axC2 = fig.add_subplot(gs[2, 1])
    keys = ["dedicated", "shared"]
    for i, k in enumerate(keys):
        sr, fd = counts_enz[k]["searched"], counts_enz[k]["found"]
        col = VIOLET if k == "dedicated" else GREY
        axC2.barh(i, sr, color=SURFACE, edgecolor=col, height=0.6, lw=1.2)
        axC2.barh(i, fd, color=col, edgecolor=col, height=0.6, lw=1.2)
        axC2.text(sr + 0.4, i, f"{sr} searched, {fd} found", va="center", fontsize=9, color=INK)
    axC2.set_yticks(range(2))
    axC2.set_yticklabels([f"{k} KOs" for k in keys], fontsize=9, color=INK)
    axC2.invert_yaxis()
    axC2.set_xlim(0, max(counts_enz[k]["searched"] for k in keys) * 1.6)
    axC2.set_title("Catalogued KOs (unique, amino-acid rows only)", loc="left", fontsize=11, color=INK)
    from matplotlib.ticker import MaxNLocator
    for ax in (axC1, axC2):
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_facecolor(SURFACE)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(RULE)
        ax.tick_params(colors=INK2, labelsize=8)

    fig.suptitle("MED4 pilot — what was searched and what was found\n"
                 "(enzyme-level preview, draft catalogue, not approved)", x=0.06, y=0.995, ha="left",
                 fontsize=14, color=INK, fontweight="bold")
    cap = ("The enzyme catalogue is a draft (drafted from standard biochemistry, not approved); KG 0.1.0-alpha.9, "
           "Prochlorococcus MED4 only. Hollow = searched, no gene annotated in MED4. Filled tiles show the MED4 locus "
           "tag(s) annotated to that KEGG KO. Shared enzymes (biosynthesis / central metabolism, including urease and "
           "Lys decarboxylase) are grey and not counted. Dashed outline = KO not present in the KG (not checked against "
           "KEGG). The broad / D-amino-acid row is never credited to an amino acid. Ile/Leu/Val and Ser/Thr share "
           "catalogue entries, so those KOs appear in more than one row. The planned analysis scores whole pathways "
           "(k of n breakdown-only steps, anchored on the step that frees N); this preview marks single enzymes only.")
    fig.text(0.06, 0.035, cap, ha="left", va="top", fontsize=8.5, color=INK2, wrap=True)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.94, bottom=0.07)
    return fig, tiles


def write_html(m, svg, tiles):
    info = {}
    for gid, idx in tiles.items():
        r = m.loc[idx]
        info[gid] = {"aa": r.amino_acid, "ko": r.ko, "enzyme": r.enzyme, "ec": r.ec, "mode": r["mode"],
                     "class": r["class"], "shared_reason": r.shared_reason,
                     "found": "yes" if r.found else "no (searched)",
                     "locus": r.genes or "-", "in_kg": "yes" if r.in_kg else "no (unchecked vs KEGG)"}
    cols = ["amino_acid", "ko", "enzyme", "ec", "mode", "shared", "class", "found", "locus_tags", "in_kg",
            "shared_reason", "kg_ko_name"]
    head = "".join(f"<th onclick=\"sortT({i})\">{html.escape(c)}</th>" for i, c in enumerate(cols))
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(r[c]))}</td>" for c in cols) + "</tr>"
                   for _, r in m.iterrows())
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>MED4 pilot: what was searched and what was found (draft)</title>
<meta name="description" content="Throwaway MED4 spike: every catalogued amino-acid N-removing enzyme, searched vs found, enzyme-level preview of a draft catalogue.">
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;background:#fcfcfb;color:#0b0b0b;max-width:1300px;margin:2rem auto;padding:0 1rem;}}
p.note{{color:#52514e;font-size:0.95rem}} svg{{max-width:100%;height:auto}}
table{{border-collapse:collapse;font-size:0.8rem;width:100%}} th,td{{border-bottom:1px solid #e3e2de;padding:3px 6px;text-align:left;vertical-align:top}}
th{{cursor:pointer;background:#f0efec}}
#tip{{position:fixed;pointer-events:none;background:#fff;border:1px solid #d6d5d0;border-radius:4px;padding:6px 8px;font-size:0.8rem;display:none;box-shadow:0 2px 6px rgba(0,0,0,.12);max-width:340px}}
g[id^="tile"]{{cursor:pointer}}
</style></head><body>
<h1>MED4 pilot &mdash; what was searched and what was found</h1>
<p class="note">Enzyme-level preview of a draft catalogue (not approved). Hollow = searched, no gene annotated in MED4.
Dashed = KO not in the KG (not checked against KEGG). The planned analysis scores whole pathways (k of n breakdown-only steps,
anchored on the step that frees N); this preview marks single enzymes only. Hover a tile in panel B for details.
Sources: spike/data/med4_n_release_catalogue.csv, spike/data/med4_aa_n_release.csv; script spike/scripts/s08_med4_pilot_matrix.py.</p>
{svg}
<div id="tip"></div>
<h2>Amino acid &times; KO matrix (med4_pilot_enzyme_matrix.csv)</h2>
<p class="note">Click a column header to sort.</p>
<table id="t"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
<script>
const INFO = {json.dumps(info)};
const tip = document.getElementById('tip');
for (const [gid, d] of Object.entries(INFO)) {{
  const g = document.getElementById(gid); if (!g) continue;
  g.addEventListener('mousemove', e => {{
    tip.innerHTML = `<b>${{d.enzyme}}</b> (${{d.ko}}, EC ${{d.ec}})<br>amino acid: ${{d.aa}}<br>N-mode: ${{d.mode}}<br>class: ${{d.class}}<br>${{d.shared_reason}}<br>found in MED4: ${{d.found}}<br>genes: ${{d.locus}}<br>KO in KG: ${{d.in_kg}}`;
    tip.style.display='block'; tip.style.left=(e.clientX+14)+'px'; tip.style.top=(e.clientY+14)+'px'; }});
  g.addEventListener('mouseleave', () => tip.style.display='none');
}}
function sortT(n){{const t=document.getElementById('t');const rows=[...t.tBodies[0].rows];
const asc=t.dataset.col==n&&t.dataset.dir!='asc';t.dataset.col=n;t.dataset.dir=asc?'asc':'desc';
rows.sort((a,b)=>{{const x=a.cells[n].textContent,y=b.cells[n].textContent;return asc?x.localeCompare(y):y.localeCompare(x)}});
rows.forEach(r=>t.tBodies[0].appendChild(r));}}
</script></body></html>"""
    (REP / "med4_pilot_matrix.html").write_text(page, encoding="utf-8")


def main():
    m = build_matrix().reset_index(drop=True)
    out = m.drop(columns=["genes"]).copy()
    out.to_csv(DATA / "med4_pilot_enzyme_matrix.csv", index=False, encoding="utf-8")
    cats = {a: row_category(m, a) for a in AAS}
    counts_aa = {c: sum(1 for a in AAS if cats[a] == c) for c in (C_DED, C_SHARED, C_NONE)}
    aa_rows = m[m.amino_acid != BROAD].drop_duplicates("ko")
    counts_enz = {}
    for k in ("dedicated", "shared"):
        s = aa_rows[aa_rows["class"] == k]
        counts_enz[k] = {"searched": len(s), "found": int(s.found.sum()),
                         "not_in_kg": int((~s.in_kg).sum())}
    fl = aa_rows[aa_rows["class"] == "flagged"]
    br = m[m.amino_acid == BROAD]
    counts_enz["flagged"] = {"searched": len(fl), "found": int(fl.found.sum())}
    counts_enz["broad"] = {"searched": len(br), "found": int(br.found.sum()), "not_in_kg": int((~br.in_kg).sum())}
    fig, tiles = draw(m, cats, counts_aa, counts_enz)
    save_figure(fig, FIG / "med4_pilot_matrix")
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", facecolor=SURFACE)
    svg = buf.getvalue()
    write_html(m, svg[svg.find("<svg"):], tiles)
    print("matrix rows:", len(m), "| unique KOs:", m.ko.nunique())
    print("amino-acid categories:", counts_aa)
    print("enzyme counts:", json.dumps(counts_enz))
    print({a: cats[a] for a in AAS})
    print("tiles with gid:", len(tiles))


if __name__ == "__main__":
    main()
