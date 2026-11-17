"""Exploration D2 / D3: per-gene trajectories of the 23 hli genes (small multiples, D1 leaf order).

Input: analysis/data/hli_gene_calls.csv, explore_D_gene_clusters.csv, explore_continuous_light_experiments.csv.
No test is recomputed.

D2  x = time since treatment start, hours (log axis). Labels parsed: "<x>h ..." -> x, "<x> min" -> x/60,
    "day <x>" -> 24x; "0h" plotted at 0.1 h (log axis). Not parseable (omitted, listed): "max across ...",
    "steady state", "acclimated", "R (rescue ...)", pooled "days 60+89".
    y = log2FC as published, one line per experiment; filled = significant call, hollow = not significant.
    Significant-only tables carry rows only for significant genes, so they contribute filled points only.
D2b same x, y = call (+1 / 0 / -1, jittered), including genes absent from significant-only tables (0)
    and leaving out not-measured cells and non-significant genes in the up-only table.
D3  x = background light level (light_control_umol; = treatment arm), the 18 continuous-light experiments,
    y = log2FC (filled = significant), all time points.
Colour + marker = stress type (fixed mapping, light and darkness merged as "light / dark");
cluster identity is on the panel title and border only.

Writes analysis/data/explore_D_trajectory_points.csv, explore_D_unparsed_timepoints.csv,
figures explore_D2_time_log2fc, explore_D2b_time_calls, explore_D3_light_level (png + svg).

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/10_explore_gene_trajectories.py
"""
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
DATA, FIG = ANALYSIS / "data", ANALYSIS / "figures"
INK, MUTED = "#1f1f1d", "#6b6b66"
CLUSTER_COL = {1: "#1baf7a", 2: "#6250d6", 3: "#e87ba4", 4: "#c98500", 5: "#008300"}
# 5 validated hues (dataviz validator, light, --pairs all: pass; CVD 6.9 -> secondary encoding = marker shape)
STYLE = {  # stress category: (colour, marker)
    "light / dark": ("#6250d6", "o"), "nitrogen": ("#1baf7a", "s"), "viral": ("#e34948", "^"),
    "iron": ("#eda100", "D"), "carbon": ("#008300", "v"), "coculture": ("#1baf7a", "P"),
    "phosphorus": ("#6250d6", "X"), "salt": ("#eda100", "h"),
}
POOLED = ("10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture", "days 60+89")
ZERO_AT = 0.1


def parse_hours(label):
    s = str(label).strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*h\b", s)
    if m:
        return float(m.group(1))
    m = re.match(r"^(\d+(?:\.\d+)?)\s*min\b", s)
    if m:
        return float(m.group(1)) / 60
    m = re.match(r"^day\s*(\d+(?:\.\d+)?)$", s, re.I)
    if m:
        return float(m.group(1)) * 24
    return np.nan


def category(st):
    return "light / dark" if st in ("light", "darkness") else st


def read(p):
    return pd.read_csv(p, encoding="utf-8", keep_default_na=False, na_values=[""])


def panels(n, ncol=6):
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(2.55 * ncol, 2.15 * nrow + 1.4), squeeze=False)
    return fig, axes


def style_panel(ax, g, cl, ckg, cc):
    ax.set_title(f"C{cl} · {g}\n{ckg} ({cc})", fontsize=7, loc="left", color=CLUSTER_COL[cl])
    for sp in ax.spines.values():
        sp.set_edgecolor(CLUSTER_COL[cl])
        sp.set_linewidth(1.2)
    ax.tick_params(labelsize=6)
    ax.axhline(0, color=MUTED, lw=0.5, zorder=0)


def legend(fig, extra):
    h = [Line2D([], [], color=c, marker=m, ls="-", lw=1, ms=5, label=k) for k, (c, m) in STYLE.items()] + extra
    fig.legend(handles=h, loc="lower center", ncol=6, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.02))


def main():
    gc = read(DATA / "hli_gene_calls.csv")
    gc = gc[~((gc.experiment_id == POOLED[0]) & (gc.timepoint == POOLED[1]))].copy()
    cl = read(DATA / "explore_D_gene_clusters.csv").sort_values("leaf_order")
    cont = set(read(DATA / "explore_continuous_light_experiments.csv").experiment_id)
    gc["hours"] = gc.timepoint.map(parse_hours)
    gc["hours_plot"] = gc.hours.replace(0, ZERO_AT)
    gc["category"] = gc.stress_type.map(category)
    gc["significant"] = gc.call.isin(["up", "down"])
    gc["call_value"] = gc.call.map({"up": 1, "down": -1, "ns": 0})
    gc.loc[(gc.up_only.astype(str) == "True") & (gc.call != "up"), "call_value"] = np.nan   # up-only table
    # phosphate 0-24 h: table filtered on q < 0.05 at 48 h, so an absent gene has no call (same rule as D1)
    gc.loc[(gc.experiment_id == "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray")
           & (gc.test_type == "descriptive") & (gc.call_source == "absent_from_significant_only_table"), "call_value"] = np.nan
    gc["continuous_light"] = gc.experiment_id.isin(cont)
    unp = gc[gc.hours.isna()][["experiment_id", "label", "timepoint"]].drop_duplicates()
    unp.to_csv(DATA / "explore_D_unparsed_timepoints.csv", index=False, encoding="utf-8")
    pts = gc[["locus_tag", "ck_group", "experiment_id", "label", "label_detailed", "stress_type", "category", "test_type",
              "timepoint", "hours", "hours_plot", "call", "call_source", "significant", "call_value", "log2fc", "padj",
              "light_control_umol", "continuous_light"]]
    pts = pts.merge(cl[["locus_tag", "cluster", "leaf_order", "copy_class"]], on="locus_tag")
    pts.to_csv(DATA / "explore_D_trajectory_points.csv", index=False, encoding="utf-8")
    genes = cl.locus_tag.tolist()
    info = cl.set_index("locus_tag")

    # ---- D2: time vs log2FC
    fig, axes = panels(len(genes))
    for ax, g in zip(axes.flat, genes):
        r = info.loc[g]
        style_panel(ax, g, r.cluster, r.ck_group, r.copy_class)
        d = pts[(pts.locus_tag == g) & pts.hours.notna() & pts.log2fc.notna()]
        for e, de in d.groupby("experiment_id"):
            de = de.sort_values("hours")
            c, m = STYLE[de.category.iloc[0]]
            if len(de) > 1:
                ax.plot(de.hours_plot, de.log2fc, color=c, lw=0.9, alpha=0.9, zorder=1)
            for rr in de.itertuples():
                ax.plot(rr.hours_plot, rr.log2fc, marker=m, ms=4, color=c, mfc=c if rr.significant else "white",
                        mec=c, mew=0.9, ls="", zorder=2)
        ax.set_xscale("log")
        ax.set_xlim(0.07, 3000)
    for ax in list(axes.flat)[len(genes):]:
        ax.set_visible(False)
    legend(fig, [Line2D([], [], marker="o", ls="", color=MUTED, label="filled = significant"),
                 Line2D([], [], marker="o", ls="", mfc="white", mec=MUTED, label="hollow = not significant")])
    fig.suptitle("hli genes over time: published log2FC per experiment (panels in D1 cluster order; x = hours since treatment "
                 "start, log scale)", fontsize=9.5, x=0.01, ha="left")
    fig.text(0.01, -0.06, "Heights are not comparable across platforms (microarray vs RNA-seq) — read only shape and timing within "
             "an experiment. Significant-only tables report only significant genes (filled points). 0 h plotted at 0.1 h. "
             f"Omitted time points (not a time): {', '.join(sorted(unp.timepoint.unique()))}.\nPooled 'days 60+89' dropped. "
             "Treatment vs control as stored (no flip). Panel title / border colour = D1 cluster.", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(FIG / "explore_D2_time_log2fc.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_D2_time_log2fc.svg", bbox_inches="tight")
    plt.close(fig)

    # ---- D2b: time vs call
    rng = np.random.default_rng(3)
    fig, axes = panels(len(genes))
    for ax, g in zip(axes.flat, genes):
        r = info.loc[g]
        style_panel(ax, g, r.cluster, r.ck_group, r.copy_class)
        d = pts[(pts.locus_tag == g) & pts.hours.notna() & pts.call_value.notna()]
        for rr in d.itertuples():
            c, m = STYLE[rr.category]
            ax.plot(rr.hours_plot * np.exp(rng.uniform(-0.12, 0.12)), rr.call_value + rng.uniform(-0.18, 0.18),
                    marker=m, ms=3.5, color=c, mfc=c if rr.significant else "white", mec=c, mew=0.8, ls="", alpha=0.85)
        ax.set_xscale("log")
        ax.set_xlim(0.07, 3000)
        ax.set_ylim(-1.4, 1.4)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(["down", "ns", "up"])
    for ax in list(axes.flat)[len(genes):]:
        ax.set_visible(False)
    legend(fig, [])
    fig.suptitle("hli genes over time: published call (+1 up / 0 not significant / −1 down, jittered); x = hours, log scale",
                 fontsize=9.5, x=0.01, ha="left")
    fig.text(0.01, -0.06, "Includes genes absent from significant-only tables (0); not-measured cells and non-significant genes "
             "in the up-only phage array are left out, as are phosphate 0–24 h genes absent from a table filtered at 48 h. 0 h plotted at 0.1 h. Panel title / border colour = D1 cluster.",
             fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(FIG / "explore_D2b_time_calls.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_D2b_time_calls.svg", bbox_inches="tight")
    plt.close(fig)

    # ---- D3: background light level vs log2FC (continuous-light experiments)
    fig, axes = panels(len(genes))
    for ax, g in zip(axes.flat, genes):
        r = info.loc[g]
        style_panel(ax, g, r.cluster, r.ck_group, r.copy_class)
        d = pts[(pts.locus_tag == g) & pts.continuous_light & pts.log2fc.notna()]
        for rr in d.itertuples():
            c, m = STYLE[rr.category]
            ax.plot(rr.light_control_umol + rng.uniform(-1.2, 1.2), rr.log2fc, marker=m, ms=4, color=c,
                    mfc=c if rr.significant else "white", mec=c, mew=0.9, ls="")
        ax.set_xlim(0, 100)
    for ax in list(axes.flat)[len(genes):]:
        ax.set_visible(False)
    legend(fig, [Line2D([], [], marker="o", ls="", color=MUTED, label="filled = significant"),
                 Line2D([], [], marker="o", ls="", mfc="white", mec=MUTED, label="hollow = not significant")])
    fig.suptitle("hli genes vs background light level (18 continuous-light experiments; x = µmol photons m⁻² s⁻¹, both arms; "
                 "y = published log2FC)", fontsize=9.5, x=0.01, ha="left")
    fig.text(0.01, -0.06, "Cells are acclimated to the background light before the treatment, and DE measures change vs a control "
             "at that same light, so light level here is context, not a treatment. Cross-study: platform, design and stress are "
             "confounded.\nHeights are not comparable across platforms. x jittered ±1.2. Panel title / border colour = D1 cluster.",
             fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(FIG / "explore_D3_light_level.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_D3_light_level.svg", bbox_inches="tight")
    plt.close(fig)
    print("points:", len(pts), "| plotted D2 (log2fc + parsed hours):", int((pts.hours.notna() & pts.log2fc.notna()).sum()),
          "| D3:", int((pts.continuous_light & pts.log2fc.notna()).sum()))
    print(unp.to_string(index=False))


if __name__ == "__main__":
    main()
