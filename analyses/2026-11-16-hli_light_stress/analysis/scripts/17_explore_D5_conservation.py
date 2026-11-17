"""Exploration D5 (A.9, exploratory): ortholog-group breadth vs response, one point per MED4 hli gene.

x = number of KG organisms in the gene's Cyanorak CK group (og_conservation.csv, 15_og_conservation.py).
y = % of the gene's defined cells called up (panel a) / down (panel b), pooled over the non-light stress
    family (display grouping A.3-A.6, so it includes coculture 2025 day 18 "N stress, control side")
    and light onset. Cells and definedness exactly as in D (explore_D_trajectory_points.csv: twin rule,
    A.8 drop, pooled days 60+89 removed, up-only phage array has no defined 'down', phosphate 0-24 h absent
    genes undefined). Descriptive time points are included, as in D.
Marker shape = D1 gene cluster; filled = multi-copy CK group, hollow = single-copy. Colour-free (ink).
Tier = grey rug square under each point (conservation.py). Deterministic dodge: points sharing an x are
spread by 0.9 organisms, ordered by cluster then locus tag.

Writes analysis/data/explore_D5_conservation.csv; figures explore_D5_conservation.{png,svg}.
Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/17_explore_D5_conservation.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import conservation as cons  # noqa: E402
import d_scheme as ds  # noqa: E402

DATA, FIG = HERE.parent / "data", HERE.parent / "figures"
INK, MUTED = "#1f1f1d", "#6b6b66"
STEP = 0.9
CTRL_SIDE = "N stress, control side"


def per_gene(p):
    rows = []
    for g, d in p.groupby("locus_tag"):
        ud, dd = d[d.up_defined], d[d.down_defined]
        rows.append(dict(locus_tag=g, n_up=int((ud.call == "up").sum()), n_up_defined=len(ud),
                         n_down=int((dd.call == "down").sum()), n_down_defined=len(dd),
                         n_experiments=d.experiment_id.nunique()))
    out = pd.DataFrame(rows)
    out["pct_up"] = 100 * out.n_up / out.n_up_defined
    out["pct_down"] = 100 * out.n_down / out.n_down_defined
    return out


def dodge(df):
    d = df.sort_values(["n_organisms", "cluster", "locus_tag"]).copy()
    d["xj"] = d.n_organisms.astype(float)
    for x, g in d.groupby("n_organisms"):
        n = len(g)
        d.loc[g.index, "xj"] = [x + (i - (n - 1) / 2) * STEP for i in range(n)]
    return d


def main():
    pts = pd.read_csv(DATA / "explore_D_trajectory_points.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    for c in ("up_defined", "down_defined"):
        pts[c] = pts[c].astype(str) == "True"
    scope = (pts.family == "stress") | (pts.type == "light onset")
    p = pts[scope]
    cl = pd.read_csv(DATA / "explore_D_gene_clusters.csv", encoding="utf-8")[["locus_tag", "cluster", "copy_class", "ck_group"]]
    a = per_gene(p)
    b = per_gene(p[p.type != CTRL_SIDE]).add_suffix("_without_control_side").rename(
        columns={"locus_tag_without_control_side": "locus_tag"})
    cg = cons.by_gene()
    d = cl.merge(cg, on="locus_tag").merge(a, on="locus_tag").merge(
        b[["locus_tag", "n_up_without_control_side", "n_up_defined_without_control_side", "pct_up_without_control_side",
           "n_down_without_control_side", "n_down_defined_without_control_side", "pct_down_without_control_side"]], on="locus_tag")
    assert len(d) == 23
    d = dodge(d)
    d["n_columns_in_scope"] = p.drop_duplicates(["experiment_id", "timepoint"]).shape[0]
    d["n_experiments_in_scope"] = p.experiment_id.nunique()
    out_cols = ["locus_tag", "ck_group", "copy_class", "cluster", "tier", "tier_name", "n_organisms", "n_pro_HL", "n_pro_LL",
                "n_synechococcus", "n_other", "med4_genes_in_group", "n_up", "n_up_defined", "pct_up", "n_down", "n_down_defined",
                "pct_down", "n_up_without_control_side", "n_up_defined_without_control_side", "pct_up_without_control_side",
                "n_down_without_control_side", "n_down_defined_without_control_side", "pct_down_without_control_side",
                "xj", "n_columns_in_scope", "n_experiments_in_scope"]
    d[out_cols].to_csv(DATA / "explore_D5_conservation.csv", index=False, encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    for ax, (yc, lab) in zip(axes, (("pct_up", "(a) % of defined cells called up"), ("pct_down", "(b) % of defined cells called down"))):
        for r in d.itertuples():
            m = ds.CLUSTER_STYLE[int(r.cluster)][1]
            multi = r.copy_class == "multi"
            ax.scatter(r.xj, getattr(r, yc), s=46, marker=m, facecolor=INK if multi else "white", edgecolor=INK, lw=1.0, zorder=3)
            ax.add_patch(Rectangle((r.xj - STEP * 0.42, -9.5), STEP * 0.84, 5, facecolor=cons.TIER_GREY[int(r.tier)],
                                   edgecolor="none", zorder=2))
        ax.axhline(0, color=MUTED, lw=0.6)
        ax.set_ylim(-11, 100)
        ax.set_yticks([0, 20, 40, 60, 80, 100])
        ax.set_xlim(15, 101)
        ax.set_xticks([21, 30, 43, 60, 80, 96])
        ax.set_xlabel("organisms in the gene's CK group (KG)", fontsize=8)
        ax.set_title(lab, fontsize=8.5, loc="left")
        ax.tick_params(labelsize=7)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.text(15.5, -7, "breadth", fontsize=5.5, color=MUTED, va="center")
    axes[0].set_ylabel("% of defined cells\n(non-light stress + light onset)", fontsize=8)
    ks = sorted(d.cluster.unique())
    h = ([Line2D([], [], ls="", label="GENE CLUSTER (D1)")]
         + [Line2D([], [], ls="", marker=ds.CLUSTER_STYLE[int(k)][1], color=INK, ms=6, label=f"   C{k}") for k in ks]
         + [Line2D([], [], ls="", label=" "), Line2D([], [], ls="", label="COPY CLASS"),
            Line2D([], [], ls="", marker="o", color=INK, ms=6, label="   multi-copy (filled)"),
            Line2D([], [], ls="", marker="o", markerfacecolor="white", markeredgecolor=INK, ms=6, label="   single-copy (hollow)"),
            Line2D([], [], ls="", label=" ")] + cons.mpl_handles())
    fig.legend(handles=h, loc="center left", bbox_to_anchor=(0.92, 0.5), fontsize=7, frameon=False)
    fig.suptitle("D5 conservation vs response (exploratory): one point per MED4 hli gene", fontsize=10, x=0.01, ha="left", y=1.02)
    fig.text(0.01, -0.06, f"Exploratory; the pattern was seen after clustering. Multi-copy twins share signal on arrays (twin rule applied). "
             f"Pool: {int(d.n_experiments_in_scope.iloc[0])} experiments, {int(d.n_columns_in_scope.iloc[0])} experiment × time points "
             f"(non-light stress family incl. coculture 2025 day 18 'N stress, control side', where down = higher under stress; + light onset).\n"
             f"Points sharing an x are dodged by {STEP} organisms (cluster, then locus tag). Grey squares under the points = ortholog-group "
             f"breadth tier. Treatment vs control as stored (no flip).", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(right=0.9, wspace=0.08)
    fig.savefig(FIG / "explore_D5_conservation.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_D5_conservation.svg", bbox_inches="tight")
    plt.close(fig)
    pd.set_option("display.width", 250)
    print(d[["locus_tag", "ck_group", "copy_class", "cluster", "tier", "n_organisms", "n_up", "n_up_defined", "pct_up", "n_down",
             "n_down_defined", "pct_down", "pct_up_without_control_side", "pct_down_without_control_side"]].to_string(index=False))


if __name__ == "__main__":
    main()
