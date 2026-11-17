"""Exploration D4: response vs time, ALL experiment x time points (including single-time-point experiments).

Input: analysis/data/explore_D_cluster_response.csv and explore_D_trajectory_points.csv (both under the twin rule
and the A.3-A.6 display overrides; written by 10_explore_gene_trajectories.py). No test recomputed, no KG query.

x = hours since treatment start (log). Time points parsed from the labels (h, min, day x 24); fixed values:
Steglich 45 min = 0.75 h; coculture 2025 day 11 = 264 h, day 18 = 432 h; lowN axenic day 14 = 336 h; coculture 2016
= 20 h; iron re-added "R (70h vs 48h)" = 70 h. "max across 70min-24h" = range bar 1.17-24 h, point at the geometric
mean (5.3 h). "steady state" / "acclimated" = a separate band at the right end. Pooled "days 60+89" dropped.
Points sharing an x are dodged deterministically in log-x (ordered by category, then experiment); in gene panels they
are also dodged vertically within the +1 / 0 / -1 rows by category. Cluster-panel point area is proportional to the
number of genes with a defined call. Colour + marker = d_scheme category (day 18 coculture = 'N stress, control side',
marker X: down there = higher in the starving control).

Writes analysis/data/explore_D4_cluster_points.csv, explore_D4_gene_points.csv, explore_D4_coincidence.csv and
figures explore_D4_clusters.{png,svg}, explore_D4_genes.{png,svg}.

Run from the repo root (after 10):
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/14_explore_D4.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d_scheme as ds  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
DATA, FIG = ANALYSIS / "data", ANALYSIS / "figures"
INK, MUTED = "#1f1f1d", "#6b6b66"
RANGE = (1.17, 24.0)
STEADY_X = 9000.0
ZERO_X = 0.3            # 0 h drawn here (log axis), tick labelled 0
DODGE = 0.045           # log10 units between dodged points
SIZE_KEY = [1, 3, 5, 9, 13]
FIXED = {"R (rescue: 70h vs 48h)": 70.0}


def x_of(tp):
    if tp in FIXED:
        return FIXED[tp], "time"
    if str(tp).startswith("max across"):
        return float(np.sqrt(RANGE[0] * RANGE[1])), "range"
    if tp in ("steady state", "acclimated"):
        return STEADY_X, "steady"
    h = ds.parse_hours(tp)
    return (h if h > 0 else ZERO_X), "time"


def read(name):
    return pd.read_csv(DATA / name, encoding="utf-8", keep_default_na=False, na_values=[""])


def columns(cr):
    c = cr.drop_duplicates(["experiment_id", "timepoint"])[["experiment_id", "label", "label_detailed", "short", "family",
                                                             "type", "timepoint", "type_rank"]].copy()
    c = c[~((c.experiment_id == ds.POOLED[0]) & (c.timepoint == ds.POOLED[1]))]
    xk = [x_of(t) for t in c.timepoint]
    c["x_base"] = [a for a, _ in xk]
    c["x_kind"] = [b for _, b in xk]
    c = c.sort_values(["x_base", "type_rank", "label"])
    c["x"] = np.nan
    for xb, g in c.groupby("x_base"):
        n = len(g)
        offs = (np.arange(n) - (n - 1) / 2) * DODGE
        c.loc[g.index, "x"] = xb * 10 ** offs
        c.loc[g.index, "n_at_same_x"] = n
    return c


def main():
    cr = read("explore_D_cluster_response.csv")
    pts = read("explore_D_trajectory_points.csv")
    cl = read("explore_D_gene_clusters.csv").sort_values("leaf_order")
    ks = sorted(cl.cluster.unique())
    cols = columns(cr)
    cp = cr.merge(cols[["experiment_id", "timepoint", "x", "x_base", "x_kind", "n_at_same_x"]], on=["experiment_id", "timepoint"])
    cp.to_csv(DATA / "explore_D4_cluster_points.csv", index=False, encoding="utf-8")
    gp = pts[~((pts.experiment_id == ds.POOLED[0]) & (pts.timepoint == ds.POOLED[1]))].copy()
    gp["value"] = [np.nan if not ds.up_defined(r) else (1 if r["call"] == "up" else -1 if (r["call"] == "down" and ds.down_defined(r))
                   else (0 if (r["call"] == "ns" and ds.down_defined(r)) else np.nan)) for r in gp.to_dict("records")]
    gp = gp.merge(cols[["experiment_id", "timepoint", "x", "x_base", "x_kind", "type_rank"]], on=["experiment_id", "timepoint"])
    nt = len(ds.TYPES)
    gp["y"] = gp.value + ((gp.type_rank - (nt - 1) / 2) / (nt - 1)) * 0.5   # vertical dodge by category, within +-0.25
    gp = gp[gp.value.notna()]
    gp.to_csv(DATA / "explore_D4_gene_points.csv", index=False, encoding="utf-8")

    # coincidence after dodging (same panel, same x and y)
    co = []
    for k in ks:
        d = cp[cp.cluster == k]
        for yc in ("pct_up", "pct_down"):
            v = d[d[yc].notna()].groupby([d.x.round(9), d[yc].round(9)]).size()
            co.append(dict(view="cluster", panel=f"C{k} {yc}", max_coincident=int(v.max()) if len(v) else 0))
    for g, d in gp.groupby("locus_tag"):
        v = d.groupby([d.x.round(9), d.y.round(9)]).size()
        co.append(dict(view="gene", panel=g, max_coincident=int(v.max())))
    co = pd.DataFrame(co)
    co.to_csv(DATA / "explore_D4_coincidence.csv", index=False, encoding="utf-8")

    def axes_x(ax):
        ax.set_xscale("log")
        ax.set_xlim(0.2, 16000)
        ax.set_xticks([ZERO_X, 1, 10, 100, 1000, STEADY_X])
        ax.set_xticklabels(["0", "1", "10", "100", "1000", "steady /\nacclim."], fontsize=6.5)
        ax.minorticks_off()
        ax.axvspan(4000, 16000, color="#f3f2ef", zorder=0)
        ax.axvline(4000, color=MUTED, lw=0.6, ls="--")

    present = set(zip(cp.family, cp.type))
    fam_h = []
    for fam in ds.FAMILY_ORDER:
        items = [(t, c, m) for (f, t), (c, m) in ds.TYPES.items() if f == fam and (f, t) in present]
        if items:
            fam_h.append(Line2D([], [], ls="", label=fam.upper()))
            fam_h += [Line2D([], [], color=c, marker=m, ls="", ms=6, label="   " + t) for t, c, m in items]

    # ---- (a) cluster panels
    fig, axes = plt.subplots(1, len(ks), figsize=(3.6 * len(ks) + 3, 4.2), sharey=True, squeeze=False)
    for ax, k in zip(axes.flat, ks):
        d = cp[cp.cluster == k]
        axes_x(ax)
        for r in d.itertuples():
            c, m = ds.TYPES[(r.family, r.type)]
            for yc, nd in (("pct_up", r.n_up_defined), ("pct_down", r.n_down_defined)):
                y = getattr(r, yc)
                if pd.isna(y):
                    continue
                if r.x_kind == "range":
                    ax.plot([RANGE[0] * r.x / r.x_base, RANGE[1] * r.x / r.x_base], [y, y], color=c, lw=1.2, alpha=0.6, zorder=1)
                ax.scatter(r.x, y, s=14 * nd, marker=m, color=c, alpha=0.7, edgecolors="white", linewidths=0.6, zorder=3)
        ax.set_ylim(-105, 105)
        ax.set_yticks([-100, -50, 0, 50, 100])
        ax.set_yticklabels(["100", "50", "0", "50", "100"], fontsize=6.5)
        ax.axhline(0, color=MUTED, lw=0.6)
        ax.set_title(f"C{k} ({int((cl.cluster == k).sum())} genes)", fontsize=8.5, loc="left", fontweight="bold")
        ax.set_xlabel("hours since treatment start (log)", fontsize=7)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0, 0].set_ylabel("% of cluster genes\n← down · up →", fontsize=7)
    size_h = [plt.scatter([], [], s=14 * n, color=MUTED, alpha=0.7, edgecolors="white", label=f"{n} genes defined") for n in SIZE_KEY]
    fig.legend(handles=fam_h + [Line2D([], [], ls="", label=" "), Line2D([], [], ls="", label="POINT AREA")] + size_h,
               loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7, frameon=False)
    fig.suptitle("hli gene clusters vs time, all experiment × time points: % of each cluster's genes up (above 0) and down "
                 "(below 0)", fontsize=9.5, x=0.01, ha="left")
    fig.text(0.01, -0.12, "x = hours since treatment start (log). Bars: 'max across 70 min–24 h' (CO2 / air), point at the geometric "
             "mean. Shaded band: steady state / acclimated (no time). Points sharing an x are dodged by a fixed log-x offset.\n"
             "Coculture 2025 day 18 (marker X, 'N stress, control side'): down = higher in the N-starving control. Twin rule "
             "applied. Same −100…+100 axis in every panel. Treatment vs control as stored (no flip).", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(FIG / "explore_D4_clusters.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_D4_clusters.svg", bbox_inches="tight")
    plt.close(fig)

    # ---- (b) gene panels
    genes = cl.locus_tag.tolist()
    nc = 6
    nr = int(np.ceil(len(genes) / nc))
    fig, axes = plt.subplots(nr, nc, figsize=(2.9 * nc + 2.6, 2.0 * nr + 1.2), sharey=True, squeeze=False)
    info = cl.set_index("locus_tag")
    for ax, g in zip(axes.flat, genes):
        d = gp[gp.locus_tag == g]
        axes_x(ax)
        for r in d.itertuples():
            c, m = ds.TYPES[(r.family, r.type)]
            ax.scatter(r.x, r.y, s=16, marker=m, color=c, alpha=0.8, edgecolors="white", linewidths=0.4, zorder=3)
        ax.set_ylim(-1.45, 1.45)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(["down", "ns", "up"], fontsize=6.5)
        for yv in (-0.5, 0.5):
            ax.axhline(yv, color="#eeede9", lw=0.6)
        ax.set_title(f"C{info.at[g, 'cluster']} · {g} · {info.at[g, 'ck_group']} ({info.at[g, 'copy_class']})", fontsize=6.6,
                     loc="left", color=INK)
        for sp in ax.spines.values():
            sp.set_edgecolor(INK)
            sp.set_linewidth(0.8)
    for ax in list(axes.flat)[len(genes):]:
        ax.set_visible(False)
    fig.legend(handles=fam_h, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7, frameon=False)
    fig.suptitle("hli genes vs time, all experiment × time points: published call (up / ns / down), D1 cluster order", fontsize=9.5,
                 x=0.01, ha="left")
    fig.text(0.01, -0.03, "Rows dodged vertically by category (fixed offsets), points sharing an x dodged in log-x. Undefined cells omitted "
             "(not measured, twin rule, up-only table non-significant, phosphate 0–24 h absent). x = hours (log); shaded band = steady "
             "state / acclimated; 'max across' plotted at 5.3 h.", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.01, 1, 0.97))
    fig.savefig(FIG / "explore_D4_genes.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_D4_genes.svg", bbox_inches="tight")
    plt.close(fig)
    print(cols[["label", "timepoint", "x_base", "x_kind", "n_at_same_x"]].drop_duplicates("x_base").to_string(index=False))
    print(co.groupby("view").max_coincident.max().to_dict())
    print(co.sort_values("max_coincident", ascending=False).head(6).to_string(index=False))


if __name__ == "__main__":
    main()
