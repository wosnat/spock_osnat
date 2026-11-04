"""THROWAWAY pilot figures (no KG calls; reads a01/a02 outputs).

(a) hot1a3_step_matrix: amino acid x catalogue step tiles for HOT1A3 (searched vs found), grouped by pathway.
(b) med4_vs_hot1a3_status: 2 x 20 tiles, per-amino-acid pathway-level status (v5 rule), package/lone marker.
Palette (inherited from the MED4 pilot): violet #6250d6 dedicated, grey #8f8e89 shared, yellow #eda100 flagged.
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/spike/alteromonas_hot1a3/scripts/a03_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
MDATA = HERE.parents[1] / "methods" / "data"
DATA, FIG = HERE / "data", HERE / "figures"
FIG.mkdir(exist_ok=True)
AAS = ["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro",
       "Ser", "Thr", "Trp", "Tyr", "Val"]
VIOLET, LVIOLET, GREY, YELLOW = "#6250d6", "#c3bbf2", "#8f8e89", "#eda100"
INK, INK2, SURFACE, RULE = "#0b0b0b", "#52514e", "#fcfcfb", "#d6d5d0"
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["svg.fonttype"] = "none"


def save(fig, stem):
    fig.savefig(FIG / f"{stem}.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    fig.savefig(FIG / f"{stem}.svg", bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def step_table(hits):
    steps = pd.read_csv(MDATA / "pathway_catalogue_steps.csv", encoding="utf-8")
    assess = pd.read_csv(MDATA / "pathway_assessability.csv", encoding="utf-8")
    unobs = set()
    for v in assess.unobservable_steps.dropna():
        unobs |= set(v.split(";"))
    excluded = set(assess[assess.status_rule.str.startswith("excluded")].pathway_id)
    cred = hits[hits.call == "credited"]
    out = []
    for r in steps.itertuples():
        h = cred[cred.step_id == r.step_id]
        kos = set(h.ko)
        pres = all(any(k in kos for k in g.split("|")) for g in str(r.ko_groups).split(";"))
        fl = hits[(hits.step_id == r.step_id) & (hits.call != "credited")]
        out.append({"amino_acid": r.amino_acid, "pathway_id": r.pathway_id, "step_id": r.step_id,
                    "step_key": r.step_key, "flag": r.flag, "is_n_freeing": bool(r.is_n_freeing), "present": pres,
                    "loci": ",".join(sorted(h.locus_tag.unique())) if pres else "",
                    "flagged_loci": ",".join(sorted(fl.locus_tag.unique())), "observable": r.step_id not in unobs,
                    "excluded": r.pathway_id in excluded, "step_order": r.step_order})
    return pd.DataFrame(out)


def fig_matrix(st, aa_status, summ, key="HOT1A3", org_full="Alteromonas macleodii HOT1A3",
               stem="hot1a3_step_matrix"):
    TW, TH, GAP, PGAP, RH = 1.0, 0.46, 0.10, 0.45, 1.32
    fig = plt.figure(figsize=(21, 24))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.07, 0.075, 0.92, 0.885])
    cells = aa_status.set_index("amino_acid")
    maxx = 0
    for i, aa in enumerate(AAS):
        y = -i * RH
        c = cells.loc[aa]
        lab = f"{aa}\n{c.cell_status}" + (f" {c.cell_k_of_n}" if isinstance(c.cell_k_of_n, str) and c.cell_k_of_n else "")
        ax.text(-0.3, y, lab, ha="right", va="center", fontsize=9, color=INK, linespacing=1.3)
        x = 0.0
        for pid, g in st[st.amino_acid == aa].groupby("pathway_id", sort=False):
            g = g.sort_values("step_order")
            x0 = x
            for r in g.itertuples():
                if r.flag == "dedicated":
                    col = VIOLET
                else:
                    col = GREY
                filled = r.present
                face = col if filled else SURFACE
                edge = col
                if not filled and r.flagged_loci:
                    face, edge = YELLOW, YELLOW
                ls = "-" if r.observable else (0, (2, 1.5))
                ax.add_patch(Rectangle((x, y - TH / 2), TW, TH, facecolor=face, edgecolor=edge, lw=1.2, linestyle=ls,
                                       hatch="////" if r.excluded else None))
                tc = "white" if (filled and col == VIOLET) else INK
                ax.text(x + TW / 2, y + 0.02, r.step_key[:11], ha="center", va="center", fontsize=5.6, color=tc)
                if r.is_n_freeing:
                    ax.text(x + TW - 0.03, y - TH / 2 + 0.03, "N", ha="right", va="bottom", fontsize=5, color=tc,
                            fontweight="bold")
                below = r.loci or (r.flagged_loci + " (flag)" if r.flagged_loci else
                                   ("not in KG" if not r.observable else ""))
                if below:
                    parts = below.split(",")
                    txt = "\n".join(parts[:2]) + ("\n+%d" % (len(parts) - 2) if len(parts) > 2 else "")
                    ax.text(x + TW / 2, y - TH / 2 - 0.03, txt, ha="center", va="top", fontsize=4.6,
                            color=INK if r.present else INK2, style="normal" if r.present else "italic",
                            linespacing=1.05)
                x += TW + GAP
            ax.text(x0, y + TH / 2 + 0.04, pid.split("_", 1)[1][:22], ha="left", va="bottom", fontsize=5.2,
                    color=INK2)
            x += PGAP
        maxx = max(maxx, x)
    ax.set_xlim(-2.6, maxx + 0.2)
    ax.set_ylim(-(len(AAS) - 1) * RH - 1.0, 0.8)
    ax.axis("off")
    h = summ[key]
    fig.suptitle(f"{org_full}: catalogue steps searched vs found (draft catalogue, not approved)\n"
                 f"Dedicated steps found {h['dedicated_steps_found']} of {h['dedicated_steps_catalogued']} catalogued "
                 f"({summ['n_observable_dedicated']} observable in the KG); complete pathways: "
                 f"{len(h['complete_pathways'])}", x=0.07, y=0.985, ha="left", fontsize=14, color=INK)
    handles = [
        Rectangle((0, 0), 1, 1, facecolor=VIOLET, edgecolor=VIOLET, label="dedicated step, found (credited gene)"),
        Rectangle((0, 0), 1, 1, facecolor=SURFACE, edgecolor=VIOLET, label="dedicated step, searched, not found"),
        Rectangle((0, 0), 1, 1, facecolor=GREY, edgecolor=GREY, label="shared step, found (not counted in k/n)"),
        Rectangle((0, 0), 1, 1, facecolor=SURFACE, edgecolor=GREY, label="shared step, searched, not found"),
        Rectangle((0, 0), 1, 1, facecolor=YELLOW, edgecolor=YELLOW, label="only flagged hits (KO/product mismatch or excluded KO)"),
        Rectangle((0, 0), 1, 1, facecolor=SURFACE, edgecolor=INK2, linestyle=(0, (2, 1.5)),
                  label="dashed = step KOs have no KG node (not assessable)"),
        Rectangle((0, 0), 1, 1, facecolor=SURFACE, edgecolor=INK2, hatch="////", label="hatched = N-neutral route, excluded"),
    ]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.07, 0.045), ncol=4, fontsize=8.5, frameon=False,
               labelcolor=INK)
    fig.text(0.07, 0.035, "Tiles are catalogue steps grouped by pathway (small grey label above each group). 'N' marks "
             "the N-freeing step. Locus tags under a tile are "
             f"{key} genes credited for it (KO match + product keyword); "
             "the row label gives the per-amino-acid cell (v5 rule: complete > partial > absent > can't be judged).",
             ha="left", va="top", fontsize=8.5, color=INK2, wrap=True)
    save(fig, stem)


def fig_compare(aa_m, aa_a, oc, rows=None, title=None, stem="med4_vs_hot1a3_status"):
    fig, ax = plt.subplots(figsize=(16, 3.9))
    fig.patch.set_facecolor(SURFACE)
    W, H, G = 1.0, 1.0, 0.12
    rows = rows or [("Prochlorococcus MED4", aa_m, "MED4"), ("Alteromonas HOT1A3", aa_a, "HOT1A3")]
    fig.set_size_inches(16, 2.6 + 1.3 * len(rows))
    for j, (name, df, okey) in enumerate(rows):
        y = -j * (H + 0.35)
        ax.text(-0.25, y + H / 2, name, ha="right", va="center", fontsize=10.5, color=INK,
                style="italic" if False else "normal")
        d = df.set_index("amino_acid")
        for i, aa in enumerate(AAS):
            x = i * (W + G)
            c = d.loc[aa]
            s = c.cell_status
            kw = dict(lw=1.3)
            if s == "complete":
                p = Rectangle((x, y), W, H, facecolor=VIOLET, edgecolor=VIOLET, **kw)
            elif s == "partial":
                p = Rectangle((x, y), W, H, facecolor=LVIOLET, edgecolor=VIOLET, **kw)
            elif s == "absent":
                p = Rectangle((x, y), W, H, facecolor="white", edgecolor=GREY, **kw)
            elif s == "can't be judged":
                p = Rectangle((x, y), W, H, facecolor="#e6e5e1", edgecolor=GREY, hatch="///", **kw)
            else:
                p = Rectangle((x, y), W, H, facecolor="#efeeea", edgecolor=GREY, linestyle=(0, (3, 2)), **kw)
            ax.add_patch(p)
            tc = "white" if s == "complete" else INK
            ax.text(x + W / 2, y + H * 0.60, aa, ha="center", va="center", fontsize=11, color=tc,
                    fontweight="bold", bbox=dict(facecolor="#e6e5e1", edgecolor="none", pad=0.6)
                    if s == "can't be judged" else None)
            if s in ("complete", "partial"):
                ax.text(x + W / 2, y + H * 0.24, c.cell_k_of_n, ha="center", va="center", fontsize=8.5, color=tc)
                o = oc[(oc.organism == okey) & (oc.pathway_id == c.cell_pathway)]
                pkg = (o.operon_call == "package").any()
                ax.add_patch(Circle((x + W - 0.15, y + H - 0.15), 0.085, facecolor=tc if pkg else "none",
                                    edgecolor=tc, lw=1.2))
            if bool(c.all_shared_route_fully_present):
                ax.add_patch(Polygon([[x, y], [x + 0.24, y], [x, y + 0.24]], closed=True, facecolor=GREY,
                                     edgecolor="none"))
    ax.set_xlim(-3.6, 20 * (W + G))
    ax.set_ylim(-(len(rows) - 1) * (H + 0.35) - 0.2, 1.15)
    ax.set_aspect("equal")
    ax.axis("off")
    from matplotlib.lines import Line2D
    handles = [Rectangle((0, 0), 1, 1, facecolor=VIOLET, edgecolor=VIOLET, label="complete (k/n dedicated steps)"),
               Rectangle((0, 0), 1, 1, facecolor=LVIOLET, edgecolor=VIOLET, label="partial (k/n)"),
               Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=GREY, label="absent (not found with these annotations)"),
               Rectangle((0, 0), 1, 1, facecolor="#e6e5e1", edgecolor=GREY, hatch="///", label="can't be judged (all-shared routes only)"),
               Rectangle((0, 0), 1, 1, facecolor="#efeeea", edgecolor=GREY, linestyle=(0, (3, 2)), label="not assessable"),
               Line2D([0], [0], marker="o", ls="none", markerfacecolor=INK, markeredgecolor=INK, label="package (dedicated gene beside transporter or other step, ±3 same strand)"),
               Line2D([0], [0], marker="o", ls="none", markerfacecolor="none", markeredgecolor=INK, label="lone gene"),
               Line2D([0], [0], marker=">", ls="none", markerfacecolor=GREY, markeredgecolor=GREY, label="corner triangle: an all-shared route is fully present")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.02), ncol=3, fontsize=8, frameon=False,
              labelcolor=INK)
    ax.set_title(title or "Amino-acid breakdown pathways, MED4 vs Alteromonas HOT1A3 (pathway-level status, draft catalogue)",
                 loc="left", fontsize=12, color=INK)
    save(fig, stem)


def main():
    hits = pd.read_csv(DATA / "hits.csv", encoding="utf-8")
    summ = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    st = step_table(hits[hits.amino_acid.isin(AAS)])
    ded = st[st.flag == "dedicated"]
    summ["n_observable_dedicated"] = int(ded.observable.sum())
    st.to_csv(DATA / "hot1a3_step_matrix.csv", index=False, encoding="utf-8")
    aa_a = pd.read_csv(DATA / "aa_status.csv", encoding="utf-8")
    aa_m = pd.read_csv(DATA / "aa_status_med4.csv", encoding="utf-8")
    oc = pd.read_csv(DATA / "operon_calls.csv", encoding="utf-8")
    fig_matrix(st, aa_a, summ)
    fig_compare(aa_m, aa_a, oc)
    print("step matrix rows:", len(st), "| dedicated steps:", len(ded), "| observable:", int(ded.observable.sum()),
          "| dedicated found:", int(ded.present.sum()), "| shared steps:", int((st.flag == "shared").sum()),
          "| shared found:", int(st[st.flag == "shared"].present.sum()))


if __name__ == "__main__":
    main()
