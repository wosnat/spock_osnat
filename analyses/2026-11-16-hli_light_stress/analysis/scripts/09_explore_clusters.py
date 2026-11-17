"""Exploration D1: do the 23 MED4 hli genes fall into response groups?

Input: analysis/data/hli_gene_calls.csv only (no test is recomputed).
Matrix: genes x experiment-timepoint, value = published call coded +1 up / -1 down / 0 not significant,
NaN where the call is not defined:
  - not measured (full or top-N table without the gene);
  - up-only table (Lindell 2007 phage array): a non-significant gene could be down, so 'ns' -> NaN (up stays +1);
  - phosphate 0-24 h (table filtered on q < 0.05 at 48 h): a gene absent from the table is NaN, not 0;
  - the pooled lowN coculture 'days 60+89' column is dropped (duplicates day 60 and day 89).
Why calls, not fold changes: fold changes are not comparable across microarray and RNA-seq, and
significant-only tables give no fold change for non-significant genes; the ternary call is the only
value defined in every column.

Distance (primary, 'agreement'): 1 - share of cells with the same call, over cells measured in both genes;
fewer than MIN_SHARED shared cells -> distance 1 (max). Robustness ('correlation'): (1 - Pearson r)/2 on
shared cells, same minimum (zero-variance pairs -> 0.5). Average linkage (UPGMA). The gene tree is cut
into K clusters (maxclust); the cut height reported is the midpoint between the K-th and (K-1)-th merge.
Columns are clustered the same way (agreement, >= MIN_SHARED shared genes).
Sensitivity: the same clustering without the six Steglich 2006 light-shift columns (5 light onset + DCMU).

Writes analysis/data/explore_D_matrix.csv, explore_D_gene_clusters.csv, explore_D_distance.csv,
explore_D_distance_correlation.csv, explore_D_column_order.csv, explore_D_cluster_robustness.csv,
explore_D_cluster_summary.csv, explore_D_cluster_ck.csv; figure explore_D1_clustered_heatmap.{png,svg}.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/09_explore_clusters.py
"""
import sys
from itertools import permutations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage  # noqa: E402
from scipy.spatial.distance import squareform  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import d_scheme as ds  # noqa: E402
DATA, FIG = ANALYSIS / "data", ANALYSIS / "figures"
UP, DOWN, NS, INK, MUTED = "#eb6834", "#2a78d6", "#d9d8d4", "#1f1f1d", "#6b6b66"
MIN_SHARED = 10
K = 4
POOLED = ("10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture", "days 60+89")
PHOSPHATE = "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray"
STEGLICH = "10.1128/JB.01097-06"
# column strip categories (blue/orange are reserved for down/up, so the strip uses the other categorical slots)
STRIP = {"light / dark": "#6b6b66", "carbon": "#1baf7a", "iron": "#eda100", "nitrogen": "#e87ba4",
         "phosphorus": "#008300", "salt": "#6250d6", "phage": "#e34948", "non-stress": "#b0afa9"}
CLUSTER_COL = {1: "#1baf7a", 2: "#6250d6", 3: "#e87ba4", 4: "#c98500", 5: "#008300"}   # not blue/orange (= down/up)
MULTI = {"CK_00002025", "CK_00002026", "CK_00002168", "CK_00002332", "CK_00043616"}


def strip_cat(r):
    fam, typ = ds.category(r)
    return f"{fam}: {typ}"


def strip_colour(cat):
    fam, typ = cat.split(": ", 1)
    return ds.TYPES[(fam, typ)][0]


def code(r):
    if r["call"] == "not_measured":
        return np.nan
    if r["up_only"] in (True, "True") and r["call"] != "up":
        return np.nan
    if (r["experiment_id"] == PHOSPHATE and r["test_type"] == "descriptive"
            and r["call_source"] == "absent_from_significant_only_table"):
        return np.nan
    return {"up": 1.0, "down": -1.0, "ns": 0.0}[r["call"]]


def dist_agreement(M):
    n = M.shape[0]
    D = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            m = ~np.isnan(M[i]) & ~np.isnan(M[j])
            if i == j:
                D[i, j] = 0
            elif m.sum() >= MIN_SHARED:
                D[i, j] = 1 - np.mean(M[i, m] == M[j, m])
    return D


def dist_correlation(M):
    n = M.shape[0]
    D = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            m = ~np.isnan(M[i]) & ~np.isnan(M[j])
            if i == j:
                D[i, j] = 0
            elif m.sum() >= MIN_SHARED:
                a, b = M[i, m], M[j, m]
                if a.std() == 0 or b.std() == 0:
                    D[i, j] = 0.5
                else:
                    D[i, j] = (1 - np.corrcoef(a, b)[0, 1]) / 2
    return D


def cluster(D, k=K):
    Z = linkage(squareform(D, checks=False), method="average")
    lab = fcluster(Z, t=k, criterion="maxclust")
    h = Z[:, 2]
    cut = (h[-k] + h[-k + 1]) / 2 if k > 1 else h[-1] + 0.01
    return Z, lab, float(cut)


def match_labels(ref, other):
    """Relabel `other` to best agree with `ref` (exhaustive over label permutations, k <= 6)."""
    ro, oo = sorted(set(ref)), sorted(set(other))
    best, bm = -1, None
    for perm in permutations(ro, len(oo)) if len(oo) <= len(ro) else [tuple(oo)]:
        mp = dict(zip(oo, perm))
        s = sum(mp[o] == r for o, r in zip(other, ref))
        if s > best:
            best, bm = s, mp
    return np.array([bm.get(o, -o) for o in other])


def main():
    gc = pd.read_csv(DATA / "hli_gene_calls.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    gc = gc[~((gc.experiment_id == POOLED[0]) & (gc.timepoint == POOLED[1]))].copy()
    gc["value"] = [code(r) for r in gc.to_dict("records")]
    gc["col"] = gc.experiment_id + "|" + gc.timepoint
    gc["ck"] = gc.ck_group.str.split(":").str[-1]
    M = gc.pivot(index="locus_tag", columns="col", values="value")
    colmeta = gc.drop_duplicates("col").set_index("col")
    empty = [c for c in M.columns if M[c].isna().all()]
    M = M.drop(columns=empty)
    genes = M.index.tolist()
    ck = gc.drop_duplicates("locus_tag").set_index("locus_tag")["ck"]
    M.to_csv(DATA / "explore_D_matrix.csv", encoding="utf-8")
    X = M.values

    Da = dist_agreement(X)
    Dc = dist_correlation(X)
    pd.DataFrame(Da, index=genes, columns=genes).to_csv(DATA / "explore_D_distance.csv", encoding="utf-8")
    pd.DataFrame(Dc, index=genes, columns=genes).to_csv(DATA / "explore_D_distance_correlation.csv", encoding="utf-8")
    Za, la, cut_a = cluster(Da)
    Zc, lc, cut_c = cluster(Dc)
    leaves = dendrogram(Za, no_plot=True)["leaves"]
    # renumber clusters 1..K in leaf order
    first = {}
    for pos, i in enumerate(leaves):
        first.setdefault(la[i], len(first) + 1)
    la = np.array([first[x] for x in la])
    lc_m = match_labels(la, lc)

    # sensitivity: without Steglich columns
    keep = [c for c in M.columns if not c.startswith(STEGLICH)]
    Ds = dist_agreement(M[keep].values)
    Zs, ls, cut_s = cluster(Ds)
    ls_m = match_labels(la, ls)
    nshared = (~np.isnan(X)).astype(int) @ (~np.isnan(X)).astype(int).T

    out = pd.DataFrame(dict(locus_tag=genes, ck_group=[ck[g] for g in genes],
                            copy_class=["multi" if ck[g] in MULTI else "single" for g in genes],
                            cluster=la, cluster_correlation=lc_m, agree_correlation=la == lc_m,
                            cluster_no_steglich=ls_m, agree_no_steglich=la == ls_m,
                            n_measured_cells=(~np.isnan(X)).sum(1),
                            min_shared_cells_with_other_gene=[int(np.sort(nshared[i])[0]) for i in range(len(genes))]))
    out["leaf_order"] = [leaves.index(i) for i in range(len(genes))]
    out = out.sort_values("leaf_order")
    params = dict(distance="1 - agreement (share of shared measured cells with the same call)", linkage="average",
                  min_shared=MIN_SHARED, k=K, cut_height_agreement=round(cut_a, 4),
                  cut_height_correlation=round(cut_c, 4), cut_height_no_steglich=round(cut_s, 4),
                  n_columns=M.shape[1], n_columns_no_steglich=len(keep), dropped_empty_columns=" | ".join(empty),
                  dropped_pooled=" | ".join(POOLED))
    out.to_csv(DATA / "explore_D_gene_clusters.csv", index=False, encoding="utf-8")
    pd.DataFrame([params]).to_csv(DATA / "explore_D_parameters.csv", index=False, encoding="utf-8")
    rob = out[["locus_tag", "ck_group", "copy_class", "cluster", "cluster_correlation", "agree_correlation",
               "cluster_no_steglich", "agree_no_steglich"]]
    rob.to_csv(DATA / "explore_D_cluster_robustness.csv", index=False, encoding="utf-8")

    # columns: cluster with agreement over genes
    # columns with fewer than MIN_SHARED defined genes cannot meet the shared-cell minimum with any other column
    # (distance 1 to all); they are set apart as 'K0 sparse' and the rest are clustered
    n_def = (~np.isnan(X)).sum(0)
    dense_idx = [i for i in range(X.shape[1]) if n_def[i] >= MIN_SHARED]
    sparse_idx = [i for i in range(X.shape[1]) if n_def[i] < MIN_SHARED]
    Xd = X[:, dense_idx]
    Dcol = dist_agreement(Xd.T)
    Zcol = linkage(squareform(Dcol, checks=False), method="average")
    cleaves = dendrogram(Zcol, no_plot=True)["leaves"]
    cols = [M.columns[dense_idx[i]] for i in cleaves] + [M.columns[i] for i in sparse_idx]
    cm = colmeta.loc[cols]
    co = pd.DataFrame(dict(col=cols, experiment_id=cm.experiment_id.values, label=cm.label.values,
                           label_detailed=cm.label_detailed.values, timepoint=cm.timepoint.values,
                           strip=[strip_cat(r) for r in cm.reset_index().to_dict("records")],
                           order=range(len(cols))))
    # column clusters: cut the column tree; K_COL chosen in 4..8 at the largest gap between merge heights
    hcol = Zcol[:, 2]
    gaps = {k: hcol[-k + 1] - hcol[-k] for k in range(4, 9)}
    k_col = max(gaps, key=gaps.get)
    cut_col = float((hcol[-k_col] + hcol[-k_col + 1]) / 2)
    lab_col = fcluster(Zcol, t=k_col, criterion="maxclust")
    lab_by_col = dict(zip([M.columns[i] for i in dense_idx], lab_col))
    first_c = {}
    for c in cols:
        if c in lab_by_col:
            first_c.setdefault(lab_by_col[c], len(first_c) + 1)
    co["col_cluster"] = [first_c[lab_by_col[c]] if c in lab_by_col else 0 for c in co.col]
    co["n_defined_genes"] = [int(n_def[list(M.columns).index(c)]) for c in co.col]
    co["short"] = [ds.short_label(a, b) for a, b in zip(co.label, co.timepoint)]
    co["family"] = [x.split(": ")[0] for x in co.strip]
    co["type"] = [x.split(": ")[1] for x in co.strip]
    co.to_csv(DATA / "explore_D_column_order.csv", index=False, encoding="utf-8")
    same_exp_adj = float(np.mean([a == b for a, b in zip(co.experiment_id[:-1], co.experiment_id.values[1:])]))
    same_type_adj = float(np.mean([a == b for a, b in zip(co.strip[:-1], co.strip.values[1:])]))
    same_tp_adj = float(np.mean([a == b for a, b in zip(co.timepoint[:-1], co.timepoint.values[1:])]))
    ccl = []
    for k, g in co.groupby("col_cluster"):
        n = len(g)
        pairs = n * (n - 1) / 2

        def share(col):
            vc = g[col].value_counts()
            return float((vc * (vc - 1) / 2).sum() / pairs) if pairs else np.nan
        ccl.append(dict(col_cluster=k, n_columns=n, n_experiments=g.experiment_id.nunique(),
                        n_categories=g.strip.nunique(), n_timepoint_labels=g.timepoint.nunique(),
                        share_pairs_same_experiment=share("experiment_id"), share_pairs_same_category=share("strip"),
                        share_pairs_same_family=share("family"), share_pairs_same_timepoint_label=share("timepoint"),
                        by_family=" | ".join(f"{a} {b}" for a, b in g.family.value_counts().items()),
                        by_category=" | ".join(f"{a} {b}" for a, b in g.strip.value_counts().items()),
                        by_experiment=" | ".join(f"{a} {b}" for a, b in g.label.value_counts().items()),
                        columns=" | ".join(g.short)))
    ccl = pd.DataFrame(ccl)
    ccl["k_col"] = k_col
    ccl["note"] = ["K0 = columns with < %d defined genes (not clustered)" % MIN_SHARED if k == 0 else "" for k in ccl.col_cluster]
    ccl["cut_height_columns"] = round(cut_col, 4)
    ccl["adjacent_pairs_same_experiment_overall"] = round(same_exp_adj, 4)
    ccl["adjacent_pairs_same_category_overall"] = round(same_type_adj, 4)
    ccl["adjacent_pairs_same_timepoint_label_overall"] = round(same_tp_adj, 4)
    ccl.to_csv(DATA / "explore_D_column_clusters.csv", index=False, encoding="utf-8")
    print(f"column clusters: k={k_col}, cut={cut_col:.4f}, gaps={ {k: round(v, 4) for k, v in gaps.items()} }")
    print(f"adjacent pairs same experiment {same_exp_adj:.3f}, same category {same_type_adj:.3f}, same timepoint {same_tp_adj:.3f}")
    print(ccl.drop(columns=["columns"]).to_string(index=False))

    # cluster summary per cluster x category
    cl = dict(zip(genes, la))
    g2 = gc[gc.col.isin(M.columns)].copy()
    g2["cluster"] = g2.locus_tag.map(cl)
    g2["category"] = [strip_cat(r) for r in g2.to_dict("records")]
    rows = []
    for (c, cat), g in g2.groupby(["cluster", "category"]):
        v = g.value.dropna()
        rows.append(dict(cluster=c, category=cat, n_genes=g.locus_tag.nunique(), n_measured_cells=len(v),
                         pct_up=100 * (v == 1).mean() if len(v) else np.nan,
                         pct_down=100 * (v == -1).mean() if len(v) else np.nan))
    pd.DataFrame(rows).to_csv(DATA / "explore_D_cluster_summary.csv", index=False, encoding="utf-8")
    ckr = []
    for c, g in out.groupby("cluster"):
        vc = g.ck_group.value_counts()
        ckr.append(dict(cluster=c, n_members=len(g), n_ck_groups=len(vc), n_multi_copy=int((g.copy_class == "multi").sum()),
                        members_sharing_ck_group_within_cluster=int(vc[vc >= 2].sum()),
                        ck_groups_with_2plus_members_here=" | ".join(f"{k} ({v})" for k, v in vc[vc >= 2].items()),
                        members=" ".join(g.locus_tag)))
    pd.DataFrame(ckr).to_csv(DATA / "explore_D_cluster_ck.csv", index=False, encoding="utf-8")

    # ---- figure D1
    order_g = [genes[i] for i in leaves]
    n_r, n_c = len(order_g), len(cols)
    fig = plt.figure(figsize=(0.17 * n_c + 6.5, 0.32 * n_r + 6.0))
    left, dw, hw = 0.30, 0.09, 0.56
    ax_d = fig.add_axes([left - dw, 0.40, dw, 0.45])
    ax = fig.add_axes([left, 0.40, hw, 0.45])
    ax_s = fig.add_axes([left, 0.855, hw, 0.02])
    ax_cd = fig.add_axes([left, 0.88, hw, 0.06])
    dendrogram(Za, orientation="left", ax=ax_d, color_threshold=0, above_threshold_color=MUTED, no_labels=True)
    ax_d.axvline(cut_a, color=INK, lw=0.6, ls="--")
    ax_d.invert_yaxis()
    ax_d.set_axis_off()
    ax_d.text(cut_a, 1.0, f"cut {cut_a:.3f}", transform=ax_d.get_xaxis_transform(), fontsize=6, ha="center",
              va="bottom", color=INK)
    dendrogram(Zcol, ax=ax_cd, color_threshold=0, above_threshold_color=MUTED, no_labels=True)
    ax_cd.set_xlim(0, 10 * len(cols))   # scipy leaf spacing is 10; sparse columns sit to the right without a tree
    ax_cd.set_axis_off()
    colour = {1.0: UP, -1.0: DOWN, 0.0: NS}
    Mo = M.loc[order_g, cols]
    for i, g in enumerate(order_g):
        for j, c in enumerate(cols):
            v = Mo.iat[i, j]
            if np.isnan(v):
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor="white", lw=0.5))
                ax.add_patch(Rectangle((j + .1, i + .1), .8, .8, facecolor="none", edgecolor="#c9c8c3", hatch="////", lw=0))
            else:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=colour[v], edgecolor="white", lw=0.5))
    cl_order = [cl[g] for g in order_g]
    for i in range(1, n_r):
        if cl_order[i] != cl_order[i - 1]:
            ax.axhline(i, color=INK, lw=1.2)
    ax.set_xlim(0, n_c)
    ax.set_ylim(n_r, 0)
    ax.set_yticks(np.arange(n_r) + .5)
    ax.set_yticklabels([f"C{cl[g]}  {g}  {ck[g]}  {'■ multi' if ck[g] in MULTI else '□ single'}" for g in order_g],
                       fontsize=6.3)
    ax.yaxis.tick_right()
    for i in range(n_r):
        if i == 0 or cl_order[i] != cl_order[i - 1]:
            ax.text(-0.6, i + 0.2, f"C{cl_order[i]}", ha="right", va="top", fontsize=8, fontweight="bold", color=INK)
    cc_order = co.col_cluster.tolist()
    for j in range(1, n_c):
        if cc_order[j] != cc_order[j - 1]:
            ax.axvline(j, color=INK, lw=1.2)
    s0 = 0
    for j in range(1, n_c + 1):
        if j == n_c or cc_order[j] != cc_order[s0]:
            ax_s.text((s0 + j) / 2, 1.15, f"K{cc_order[s0]}" if cc_order[s0] else "K0 sparse", ha="center", va="bottom", fontsize=7, fontweight="bold",
                      color=INK, transform=ax_s.transData)
            s0 = j
    ax.set_xticks(np.arange(n_c) + .5)
    ax.set_xticklabels(co.short, rotation=90, fontsize=5.5)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    for j, s in enumerate(co.strip):
        ax_s.add_patch(Rectangle((j, 0), 1, 1, facecolor=strip_colour(s), edgecolor="white", lw=0.4))
    ax_s.set_xlim(0, n_c)
    ax_s.set_ylim(0, 1)
    ax_s.set_axis_off()
    fig.legend(handles=[Patch(facecolor=UP, label="up (+1)"), Patch(facecolor=DOWN, label="down (−1)"),
                        Patch(facecolor=NS, label="not significant (0)"),
                        Patch(facecolor="white", edgecolor="#c9c8c3", hatch="////", label="not defined (NaN)")]
               + [Patch(facecolor=c, label=f"{fam}: {typ}") for (fam, typ), (c, m) in ds.TYPES.items()],
               loc="upper left", bbox_to_anchor=(left + hw + 0.12, 0.85), fontsize=6.5, frameon=False)
    fig.text(0.01, 1.01, f"hli genes (MED4) clustered by their published calls across {n_c} experiment × time-point columns",
             fontsize=10, va="top")
    fig.text(0.01, 0.99, f"Gene distance = 1 − agreement over cells defined in both genes (≥{MIN_SHARED} shared, else 1); "
             f"average linkage; cut at {cut_a:.3f} → {K} gene clusters (C1–C{K}). Columns clustered the same way, cut at "
             f"{cut_col:.3f} → {k_col} column clusters (K1–K{k_col}).",
             fontsize=7, va="top", color=MUTED)
    fig.text(left, 0.035, "Value = published call (+1 / 0 / −1). NaN: not measured; up-only phage array (non-significant could be "
             "down); phosphate 0–24 h genes absent from a table filtered at 48 h.\nPooled 'days 60+89' dropped. "
             "Treatment vs control as stored (no flip). Multi-copy = CK group with ≥2 MED4 hli members.",
             fontsize=6.3, color=MUTED, va="bottom")
    fig.savefig(FIG / "explore_D1_clustered_heatmap.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_D1_clustered_heatmap.svg", bbox_inches="tight")
    plt.close(fig)
    pd.set_option("display.width", 220)
    print(params)
    print(rob.to_string(index=False))
    print(pd.DataFrame(ckr).to_string(index=False))


if __name__ == "__main__":
    main()
