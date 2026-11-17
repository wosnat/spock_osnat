"""Exploration D2 / D3: how each hli gene cluster (D1, C1-C4) responds over time and across background light.

Input: analysis/data/hli_gene_calls.csv, explore_D_gene_clusters.csv, explore_continuous_light_experiments.csv
(no test recomputed). Per experiment x timepoint x gene cluster:
  % up   = 100 x (genes called up) / (genes where 'up or not' is defined)
  % down = -100 x (genes called down) / (genes where 'down or not' is defined)   (plotted below zero)
'Defined' follows D1: not measured -> undefined; phosphate 0-24 h genes absent from the 48 h-filtered table ->
undefined; in the up-only phage array 'down' is undefined (so % down is not plotted there).
y axis fixed at -100..+100 in every panel. No log2FC on any axis (log2FC only in the hover data).

D2  one panel per time-course experiment (>= 3 parseable time points; pooled 'days 60+89' dropped);
    x = hours since treatment start (log). One line per cluster (ink; line style + marker + direct label).
    Header strip = experiment category colour (d_scheme). Companion: per experiment, genes (cluster order) x time.
D3  the 18 continuous-light experiments; x = background light (light_control_umol, both arms);
    one panel per cluster; points = experiment x time point, colour + marker = category (d_scheme).
    Companion: genes (cluster order) x experiment-time point ordered by light level.

Writes analysis/data/explore_D_cluster_response.csv, explore_D_trajectory_points.csv,
explore_D_unparsed_timepoints.csv, explore_D_timecourse_experiments.csv; figures explore_D2_cluster_time,
explore_D2_gene_time, explore_D3_cluster_light, explore_D3_gene_light (png + svg).

Run from the repo root (after 09):
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/10_explore_gene_trajectories.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d_scheme as ds  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
DATA, FIG = ANALYSIS / "data", ANALYSIS / "figures"
UP, DOWN, NS, INK, MUTED = "#eb6834", "#2a78d6", "#d9d8d4", "#1f1f1d", "#6b6b66"
YT = [-100, -50, 0, 50, 100]


def read(p):
    """Read a CSV; display overrides (A.3-A.6: labels and grouping only) applied in memory."""
    import sys as _s
    _s.path.insert(0, str(Path(__file__).resolve().parent))
    import display_overrides as dov
    return dov.apply(pd.read_csv(p, encoding="utf-8", keep_default_na=False, na_values=[""]))


def save(fig, stem):
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def family_handles(types_present=None):
    h = []
    for fam in ds.FAMILY_ORDER:
        items = [(t, c, m) for (f, t), (c, m) in ds.TYPES.items()
                 if f == fam and (types_present is None or (f, t) in types_present)]
        if not items:
            continue
        h.append(Line2D([], [], ls="", label=fam.upper()))
        for t, c, m in items:
            h.append(Line2D([], [], color=c, marker=m, ls="", ms=6, label="   " + t))
    return h


def cluster_handles(ks):
    return [Line2D([], [], color=INK, ls=ds.CLUSTER_STYLE[k][0], marker=ds.CLUSTER_STYLE[k][1], ms=5, lw=1.3,
                   label=f"C{k}") for k in ks]


def main():
    gc = read(DATA / "hli_gene_calls.csv")
    gc = gc[~((gc.experiment_id == ds.POOLED[0]) & (gc.timepoint == ds.POOLED[1]))].copy()
    cl = read(DATA / "explore_D_gene_clusters.csv").sort_values("leaf_order")
    cmap = dict(zip(cl.locus_tag, cl.cluster))
    ks = sorted(cl.cluster.unique())
    cont = read(DATA / "explore_continuous_light_experiments.csv")
    gc["cluster"] = gc.locus_tag.map(cmap)
    gc["hours"] = gc.timepoint.map(ds.parse_hours)
    cat = [ds.category(r) for r in gc.to_dict("records")]
    gc["family"] = [c[0] for c in cat]
    gc["type"] = [c[1] for c in cat]
    gc["up_defined"] = [ds.up_defined(r) for r in gc.to_dict("records")]
    gc["down_defined"] = [ds.down_defined(r) for r in gc.to_dict("records")]
    gc["continuous_light"] = gc.experiment_id.isin(set(cont.experiment_id))
    gc["short"] = [ds.short_label(a, b) for a, b in zip(gc.label, gc.timepoint)]
    gc.drop(columns=[]).to_csv(DATA / "explore_D_trajectory_points.csv", index=False, encoding="utf-8")
    gc[gc.hours.isna()][["experiment_id", "label", "timepoint"]].drop_duplicates().to_csv(
        DATA / "explore_D_unparsed_timepoints.csv", index=False, encoding="utf-8")

    rows = []
    for (e, tp, k), g in gc.groupby(["experiment_id", "timepoint", "cluster"], sort=False):
        ud, dd = g[g.up_defined], g[g.down_defined]
        nu, nd = int((ud.call == "up").sum()), int((dd.call == "down").sum())
        r0 = g.iloc[0]
        rows.append(dict(experiment_id=e, label=r0.label, label_detailed=r0.label_detailed, short=r0.short,
                         family=r0.family, type=r0.type, timepoint=tp, timepoint_order=r0.timepoint_order,
                         hours=r0.hours, light_umol=r0.light_control_umol, continuous_light=bool(r0.continuous_light),
                         test_type=r0.test_type, cluster=k, n_genes=len(g), n_up_defined=len(ud),
                         n_down_defined=len(dd), n_up=nu, n_down=nd,
                         pct_up=100 * nu / len(ud) if len(ud) else np.nan,
                         pct_down=-100 * nd / len(dd) if len(dd) else np.nan,
                         genes_up=" ".join(ud[ud.call == "up"].locus_tag), genes_down=" ".join(dd[dd.call == "down"].locus_tag)))
    cr = pd.DataFrame(rows)
    cr["type_rank"] = [ds.type_rank(f, t) for f, t in zip(cr.family, cr.type)]
    cr.to_csv(DATA / "explore_D_cluster_response.csv", index=False, encoding="utf-8")

    ntp = cr[cr.hours.notna()].groupby("experiment_id").timepoint.nunique()
    tc = cr[cr.experiment_id.isin(ntp[ntp >= 3].index)]
    exps = (tc.drop_duplicates("experiment_id").sort_values(["type_rank", "label"])[
        ["experiment_id", "label", "label_detailed", "family", "type"]])
    exps["n_timepoints"] = exps.experiment_id.map(ntp)
    exps.to_csv(DATA / "explore_D_timecourse_experiments.csv", index=False, encoding="utf-8")

    # ---- D2: cluster response over time
    n = len(exps)
    ncol = 4
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.6 * ncol, 2.9 * nrow + 1.6), squeeze=False, sharey=True)
    for ax, er in zip(axes.flat, exps.itertuples()):
        d = tc[tc.experiment_id == er.experiment_id]
        col = ds.TYPES[(er.family, er.type)][0]
        ends = []
        for k in ks:
            dk = d[d.cluster == k].sort_values("hours")
            ls, mk = ds.CLUSTER_STYLE[k]
            x = dk.hours.replace(0, 0.1)
            for yc in ("pct_up", "pct_down"):
                ok = dk[yc].notna()
                if ok.any():
                    ax.plot(x[ok], dk[yc][ok], color=INK, ls=ls, marker=mk, ms=3.8, lw=1.1, mfc="white" if yc == "pct_down" else INK)
            ok = dk.pct_up.notna()
            if ok.any():
                ends.append([dk.pct_up[ok].iloc[-1], k, x[ok].iloc[-1]])
        ends.sort()
        for i in range(1, len(ends)):   # spread direct labels so they do not overlap
            ends[i][0] = max(ends[i][0], ends[i - 1][0] + 11)
        for y, k, x0 in ends:
            ax.annotate(f"C{k}", (x0, y), xytext=(5, 0), textcoords="offset points", fontsize=6, color=INK, va="center")
        ax.set_xscale("log")
        xs = sorted(d.hours.replace(0, 0.1).unique())
        ax.set_xticks(xs)
        ax.set_xticklabels([("0" if v == 0.1 else f"{v:g}") for v in xs], fontsize=5.8, rotation=0)
        ax.minorticks_off()
        ax.set_xlim(min(xs) / 1.6, max(xs) * 2.2)
        ax.set_ylim(-105, 105)
        ax.set_yticks(YT)
        ax.set_yticklabels([str(abs(v)) for v in YT], fontsize=6.5)
        ax.axhline(0, color=MUTED, lw=0.6)
        ax.set_xlabel("hours since treatment start (log; 0 h at 0.1)", fontsize=6.3)
        ax.add_patch(Rectangle((0, 1.0), 1, 0.13, transform=ax.transAxes, facecolor=col, clip_on=False))
        ax.text(0.01, 1.065, f"{ds.SHORT.get(er.label, er.label)}  ·  {er.type}", transform=ax.transAxes, fontsize=7, color="white", va="center",
                fontweight="bold")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    for ax in list(axes.flat)[n:]:
        ax.set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel("% of cluster genes\n← down · up →", fontsize=7)
    present = set(zip(exps.family, exps.type))
    fig.legend(handles=cluster_handles(ks) + [Line2D([], [], ls="", label=" ")] + family_handles(present),
               loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7, frameon=False,
               title="Gene clusters (D1)          Category (header colour)", title_fontsize=7)
    fig.suptitle("hli gene clusters over time: % of each cluster's genes called up (above 0, filled markers) and down "
                 "(below 0, open markers), per time-course experiment", fontsize=9.5, x=0.01, ha="left")
    fig.text(0.01, -0.03, "Same y axis (−100 to +100 %) in every panel. Denominator = genes with a defined call (not measured, "
             "phosphate 0–24 h genes absent from a 48 h-filtered table, and 'down' in the up-only phage array are undefined).\n"
             "Treatment vs control as stored (no flip). Experiments with ≥3 parseable time points; pooled 'days 60+89' dropped.",
             fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    save(fig, FIG / "explore_D2_cluster_time")

    # ---- D2 companion: gene-level heatmap per time-course experiment
    genes = cl.locus_tag.tolist()
    fig, axes = plt.subplots(1, n, figsize=(0.32 * tc.groupby("experiment_id").timepoint.nunique().sum() + 3.5, 6.6),
                             sharey=True, gridspec_kw=dict(width_ratios=[max(2, ntp[e]) for e in exps.experiment_id]))
    for ax, er in zip(np.atleast_1d(axes), exps.itertuples()):
        g = gc[gc.experiment_id == er.experiment_id]
        tps = g[["timepoint", "hours"]].drop_duplicates().dropna().sort_values("hours")
        gi = g.set_index(["locus_tag", "timepoint"])
        for j, tp in enumerate(tps.timepoint):
            for i, gn in enumerate(genes):
                r = gi.loc[(gn, tp)]
                undefined = not r["up_defined"] or (r["call"] != "up" and not r["down_defined"])
                if undefined:
                    ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor="white"))
                    ax.add_patch(Rectangle((j + .12, i + .12), .76, .76, facecolor="none", edgecolor="#c9c8c3", hatch="////", lw=0))
                else:
                    ax.add_patch(Rectangle((j, i), 1, 1, facecolor={"up": UP, "down": DOWN, "ns": NS}[r["call"]],
                                           edgecolor="white", lw=0.6))
        for i in range(1, len(genes)):
            if cmap[genes[i]] != cmap[genes[i - 1]]:
                ax.axhline(i, color=INK, lw=1.1)
        ax.set_xlim(0, len(tps))
        ax.set_ylim(len(genes), 0)
        ax.set_xticks(np.arange(len(tps)) + .5)
        ax.set_xticklabels([ds.short_tp(t) for t in tps.timepoint], rotation=90, fontsize=6)
        ax.tick_params(length=0)
        col = ds.TYPES[(er.family, er.type)][0]
        ax.add_patch(Rectangle((0, -1.3), len(tps), 1.1, facecolor=col, clip_on=False))
        ax.set_title(ds.SHORT.get(er.label, er.label), fontsize=7, pad=14)
        for sp in ax.spines.values():
            sp.set_visible(False)
    a0 = np.atleast_1d(axes)[0]
    a0.set_yticks(np.arange(len(genes)) + .5)
    a0.set_yticklabels([f"C{cmap[g]} {g}" for g in genes], fontsize=6.3)
    fig.legend(handles=[Patch(facecolor=UP, label="up"), Patch(facecolor=DOWN, label="down"), Patch(facecolor=NS, label="not significant"),
                        Patch(facecolor="white", edgecolor="#c9c8c3", hatch="////", label="not defined"),
                        Line2D([], [], ls="", label=" ")] + family_handles(present),
               loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7, frameon=False)
    fig.suptitle("hli genes (D1 cluster order) × time points in time order, per time-course experiment (header colour = category)",
                 fontsize=9.5, x=0.01, ha="left")
    save(fig, FIG / "explore_D2_gene_time")

    # ---- D3: cluster response vs background light (continuous-light experiments)
    lc = cr[cr.continuous_light].copy()
    rng = np.random.default_rng(5)
    lc["xj"] = lc.light_umol + rng.uniform(-1.5, 1.5, len(lc))
    fig, axes = plt.subplots(1, len(ks), figsize=(3.4 * len(ks) + 2.8, 3.8), sharey=True, squeeze=False)
    for ax, k in zip(axes.flat, ks):
        d = lc[lc.cluster == k]
        for r in d.itertuples():
            c, m = ds.TYPES[(r.family, r.type)]
            if not np.isnan(r.pct_up):
                ax.plot(r.xj, r.pct_up, marker=m, ms=5, color=c, mec="white", mew=0.5, ls="")
            if not np.isnan(r.pct_down):
                ax.plot(r.xj, r.pct_down, marker=m, ms=5, color=c, mec="white", mew=0.5, ls="")
        ax.set_ylim(-105, 105)
        ax.set_yticks(YT)
        ax.set_yticklabels([str(abs(v)) for v in YT], fontsize=6.5)
        ax.axhline(0, color=MUTED, lw=0.6)
        ax.set_xlim(0, 100)
        ax.set_xlabel("background light, µmol photons m⁻² s⁻¹", fontsize=7)
        ax.tick_params(labelsize=6.5)
        ax.set_title(f"C{k} ({int((cl.cluster == k).sum())} genes)", fontsize=8.5, loc="left", fontweight="bold", color=INK)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(INK)
    axes[0, 0].set_ylabel("% of cluster genes\n← down · up →", fontsize=7)
    present3 = set(zip(lc.family, lc.type))
    fig.legend(handles=family_handles(present3), loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7, frameon=False,
               title="Category", title_fontsize=7)
    fig.suptitle("hli gene clusters vs background light: % of each cluster's genes called up (above 0) and down (below 0), "
                 "per experiment × time point, 18 continuous-light experiments", fontsize=9.5, x=0.01, ha="left")
    fig.text(0.01, -0.1, "Cells are acclimated to the background light before the treatment, and DE measures change vs a control at "
             "that same light, so light level here is context, not a treatment. Cross-study: platform, design and stress are "
             "confounded.\nSame y axis (−100 to +100 %) in every panel; x jittered ±1.5. Treatment vs control as stored (no flip).",
             fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.0, 1, 0.92))
    save(fig, FIG / "explore_D3_cluster_light")

    # ---- D3 companion: genes x continuous-light experiment-timepoints ordered by light
    cols = (gc[gc.continuous_light][["experiment_id", "label", "timepoint", "timepoint_order", "light_control_umol",
                                      "family", "type", "short"]].drop_duplicates(["experiment_id", "timepoint"])
            .sort_values(["light_control_umol", "label", "timepoint_order"]))
    gi = gc.set_index(["locus_tag", "experiment_id", "timepoint"])
    fig, ax = plt.subplots(figsize=(0.2 * len(cols) + 4, 6.8))
    for j, c in enumerate(cols.itertuples()):
        for i, gn in enumerate(genes):
            r = gi.loc[(gn, c.experiment_id, c.timepoint)]
            undefined = not r["up_defined"] or (r["call"] != "up" and not r["down_defined"])
            if undefined:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor="white"))
                ax.add_patch(Rectangle((j + .12, i + .12), .76, .76, facecolor="none", edgecolor="#c9c8c3", hatch="////", lw=0))
            else:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor={"up": UP, "down": DOWN, "ns": NS}[r["call"]], edgecolor="white", lw=0.6))
        ax.add_patch(Rectangle((j, -1.3), 1, 1.0, facecolor=ds.TYPES[(c.family, c.type)][0], edgecolor="white", lw=0.4, clip_on=False))
    lv = cols.light_control_umol.tolist()
    s0 = 0
    for j in range(1, len(cols) + 1):
        if j == len(cols) or lv[j] != lv[s0]:
            if j < len(cols):
                ax.axvline(j, color=INK, lw=1.0)
            ax.text((s0 + j) / 2, -1.6, f"{lv[s0]:g}", ha="center", va="bottom", fontsize=6.5)
            s0 = j
    for i in range(1, len(genes)):
        if cmap[genes[i]] != cmap[genes[i - 1]]:
            ax.axhline(i, color=INK, lw=1.1)
    ax.set_xlim(0, len(cols))
    ax.set_ylim(len(genes), 0)
    ax.set_yticks(np.arange(len(genes)) + .5)
    ax.set_yticklabels([f"C{cmap[g]} {g}" for g in genes], fontsize=6.3)
    ax.set_xticks(np.arange(len(cols)) + .5)
    ax.set_xticklabels(cols.short, rotation=90, fontsize=6)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.legend(handles=[Patch(facecolor=UP, label="up"), Patch(facecolor=DOWN, label="down"), Patch(facecolor=NS, label="not significant"),
                        Patch(facecolor="white", edgecolor="#c9c8c3", hatch="////", label="not defined"),
                        Line2D([], [], ls="", label=" ")] + family_handles(present3),
               loc="center left", bbox_to_anchor=(0.92, 0.5), fontsize=7, frameon=False)
    ax.set_title("hli genes (D1 cluster order) × continuous-light experiment-time points, ordered by background light "
                 "(block label, µmol); strip = category", fontsize=9, loc="left", pad=22)
    save(fig, FIG / "explore_D3_gene_light")
    print(exps.to_string(index=False))
    print("cluster_response rows:", len(cr))


if __name__ == "__main__":
    main()
