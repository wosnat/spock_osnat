"""Exploration E, step 2 (exploratory, no tests): the 23 MED4 hli genes in the KG's diel sources.

Inputs (from 22_explore_diel_pull.py): explore_E_cluster_analysis.csv (Mfuzz analysis + its 18 clusters),
explore_E_cluster_membership.csv (hli memberships), explore_E_derived_metrics.csv (Waldbauer 2012 metrics for hli:
0 rows), explore_E_de_rows.csv (Zinser 2009 DE rows: 0 rows); plus D clusters (explore_D_gene_clusters.csv) and the
conservation tiers (conservation.py).

Peak phase: the KG states a phase only in each cluster's temporal_pattern text ("near X hours after onset of dark");
X is parsed as stated_peak_h. Cluster 1 states "8.3 h in the paper's time scale" (a different scale): kept as text, not
placed on the axis. No light/dark shading: the KG gives the 14:10 L:D cycle but the stated time origin ("onset of
dark") does not agree with the clusters' own day-part labels, so light/dark periods cannot be placed from KG fields.

Writes analysis/data/explore_E_diel_clusters_all.csv (18 clusters), explore_E_hli_diel.csv (23 genes),
explore_E_summary_by_D_cluster.csv; figure explore_E1_diel_phase.{png,svg}.
Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/22_explore_diel_figs.py
"""
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import conservation as cons  # noqa: E402

DATA, FIG = HERE.parent / "data", HERE.parent / "figures"
INK, MUTED = "#1f1f1d", "#6b6b66"
W = 7.2
plt.rcParams.update({"font.size": 8, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
                     "svg.fonttype": "none", "axes.linewidth": 0.6})


def rd(n):
    return pd.read_csv(DATA / n, encoding="utf-8", keep_default_na=False, na_values=[""])


def main():
    an = rd("explore_E_cluster_analysis.csv").iloc[0]
    cl = pd.DataFrame(json.loads(an.clusters))
    cl["diel_cluster"] = cl.cluster_id.str.split(":").str[-1].astype(int)
    cl["stated_peak_h"] = [float(m.group(1)) if isinstance(t, str) and (m := re.search(r"near ([\d.]+) hours after onset of dark", t))
                           else np.nan for t in cl.temporal_pattern]
    cl = cl.sort_values("diel_cluster")
    cl[["diel_cluster", "cluster_id", "name", "member_count", "expression_dynamics", "temporal_pattern", "stated_peak_h",
        "functional_description"]].to_csv(DATA / "explore_E_diel_clusters_all.csv", index=False, encoding="utf-8")
    mem = rd("explore_E_cluster_membership.csv")
    assert rd("explore_E_derived_metrics.csv").empty if (DATA / "explore_E_derived_metrics.csv").stat().st_size > 2 else True
    dc = rd("explore_D_gene_clusters.csv").sort_values("leaf_order")
    cg = cons.by_gene().set_index("locus_tag")
    ci = cl.set_index("cluster_id")
    rows = []
    for r in dc.itertuples():
        m = mem[mem.locus_tag == r.locus_tag]
        base = dict(locus_tag=r.locus_tag, ck_group=r.ck_group, copy_class=r.copy_class, D_cluster=int(r.cluster),
                    tier=int(cg.at[r.locus_tag, "tier"]), tier_name=cons.TIER_NAME[int(cg.at[r.locus_tag, "tier"])],
                    n_organisms=int(cg.at[r.locus_tag, "n_organisms"]))
        if len(m):
            assert len(m) == 1
            m0 = m.iloc[0]
            c = ci.loc[m0.cluster_id]
            base.update(in_diel_cluster=True, diel_cluster=int(c.diel_cluster), membership_score=float(m0.membership_score),
                        diel_cluster_size=int(c.member_count), expression_dynamics=c.expression_dynamics,
                        temporal_pattern=c.temporal_pattern, stated_peak_h=c.stated_peak_h, cluster_name=c["name"])
        else:
            base.update(in_diel_cluster=False, diel_cluster=np.nan, membership_score=np.nan, diel_cluster_size=np.nan,
                        expression_dynamics=None, temporal_pattern=None, stated_peak_h=np.nan, cluster_name=None)
        base.update(waldbauer_peak_time_transcript_h=np.nan, waldbauer_diel_amplitude_transcript_log2=np.nan,
                    waldbauer_peak_time_protein_h=np.nan, waldbauer_note="hli gene not among the 312 Waldbauer 2012 genes")
        rows.append(base)
    g = pd.DataFrame(rows)
    g.to_csv(DATA / "explore_E_hli_diel.csv", index=False, encoding="utf-8")
    s = []
    for k, d in g.groupby("D_cluster"):
        mix = d.diel_cluster.dropna().astype(int).value_counts().sort_index()
        s.append(dict(D_cluster=k, n_genes=len(d), n_in_diel_cluster=int(d.in_diel_cluster.sum()),
                      n_with_stated_peak=int(d.stated_peak_h.notna().sum()), median_stated_peak_h=d.stated_peak_h.median(),
                      peaks=" ".join(f"{v:g}" for v in d.stated_peak_h.dropna()),
                      diel_cluster_mix=" | ".join(f"diel {a} ({b})" for a, b in mix.items()),
                      not_in_diel_cluster=" ".join(d[~d.in_diel_cluster].locus_tag),
                      n_waldbauer=0, median_amplitude="not available (no hli gene in Waldbauer 2012)"))
    s = pd.DataFrame(s)
    s.to_csv(DATA / "explore_E_summary_by_D_cluster.csv", index=False, encoding="utf-8")

    # ---- E1: stated cluster peak phase per gene (D1 order)
    genes = g.locus_tag.tolist()
    nr = len(genes)
    H = 5.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([2.0 / W, 1.0 / H, 2.9 / W, (H - 1.45) / H])
    for i, r in g.iterrows():
        ax.axhline(i + 0.5, color="#eeede9", lw=0.6, zorder=0)
        if not np.isnan(r.stated_peak_h):
            ms = 4 + 6 * r.membership_score
            ax.plot(r.stated_peak_h, i + 0.5, marker="o", ms=ms, mfc=INK if r.copy_class == "multi" else "white", mec=INK,
                    mew=1.0, ls="", zorder=3)
        txt = (f"diel {int(r.diel_cluster)}: " + (r.expression_dynamics if isinstance(r.expression_dynamics, str) else "no phase in KG") if r.in_diel_cluster
               else "not in a diel cluster")
        if r.in_diel_cluster and r.diel_cluster == 1:
            txt = "diel 1: midday (8.3 h, other scale)"
        ax.text(24.8, i + 0.5, txt, va="center", ha="left", fontsize=8, color=INK if r.in_diel_cluster else MUTED)
    ax.set_xlim(0, 24)
    ax.set_ylim(nr, 0)
    ax.set_xticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_xlabel("stated cluster peak, h after onset of dark")
    ax.set_yticks(np.arange(nr) + 0.5)
    ax.set_yticklabels(genes)
    ax.tick_params(axis="y", length=0, pad=14)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    tr = ax.get_yaxis_transform()
    for i, r in g.iterrows():
        ax.add_patch(Rectangle((-0.035, i + 0.12), 0.022, 0.76, facecolor=cons.TIER_GREY[r.tier], transform=tr, clip_on=False))
    cls = g.D_cluster.tolist()
    s0 = 0
    for i in range(1, nr + 1):
        if i == nr or cls[i] != cls[s0]:
            ax.plot([-0.4, -0.4], [s0 + 0.15, i - 0.15], color=INK, lw=1.0, transform=tr, clip_on=False)
            ax.text(-0.42, (s0 + i) / 2, f"C{cls[s0]}", ha="right", va="center", fontsize=8, fontweight="bold", transform=tr)
            if i < nr:
                ax.axhline(i, color=INK, lw=0.8)
            s0 = i
    fig.legend(handles=[Line2D([], [], marker="o", ls="", mfc=INK, mec=INK, ms=7, label="multi-copy"),
                        Line2D([], [], marker="o", ls="", mfc="white", mec=INK, ms=7, label="single-copy"),
                        Line2D([], [], marker="o", ls="", mfc="white", mec=INK, ms=4.6, label="membership 0.1"),
                        Line2D([], [], marker="o", ls="", mfc="white", mec=INK, ms=10, label="membership 1.0")]
               + [Patch(facecolor=cons.TIER_GREY[t], label=cons.TIER_SHORT[t]) for t in cons.TIER_NAME],
               loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=4, frameon=False, fontsize=8, columnspacing=1.0)
    fig.text(0.01, 0.995, "Peak = the Mfuzz diel cluster's stated phase (KG cluster text), not a per-gene value. "
             "No light/dark shading: see note.", fontsize=8, va="top", color=MUTED)
    fig.savefig(FIG / "explore_E1_diel_phase.png", dpi=300)
    fig.savefig(FIG / "explore_E1_diel_phase.svg")
    plt.close(fig)
    pd.set_option("display.width", 250)
    print(cl[["diel_cluster", "member_count", "expression_dynamics", "stated_peak_h"]].to_string(index=False))
    print("cluster member_count sum:", int(cl.member_count.sum()), "| analysis total_gene_count:", an.total_gene_count)
    print(g[["locus_tag", "D_cluster", "copy_class", "tier", "diel_cluster", "membership_score", "expression_dynamics",
             "stated_peak_h"]].to_string(index=False))
    print(s.to_string(index=False))


if __name__ == "__main__":
    main()
