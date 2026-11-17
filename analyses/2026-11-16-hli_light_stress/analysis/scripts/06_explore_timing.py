"""Exploration C: timing of the hli response in time-course experiments.

Experiments with >= 3 timepoints, plus extended light / extended darkness (2 timepoints, flagged).
Timepoint labels parsed to hours: "<x>h ..." -> x; "<x> min" -> x/60; "day <x>" -> 24x. Labels that
are not a time ("days 60+89" pooled, "max across ...", "steady state", ...) are kept off the time axis.

For hli and every reference set, per timepoint: share of measured set genes significant up / down
(gene calls on the main background with methods' gene_calls_from_background, from the KG DE rows),
the set-level BH padj per direction and the testable flags (from analysis/data/hli_tests.csv).

Writes analysis/data/explore_timing.csv, explore_timing_summary.csv, explore_timing_labels.csv and
figures explore_C1_timing.{png,svg}, explore_C2_gene_time.{png,svg}.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/06_explore_timing.py
"""
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
from multiomics_explorer import GraphConnection  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
METHODS = ANALYSIS.parent / "methods"
sys.path.insert(0, str(METHODS))
import hli_scoring as hs  # noqa: E402
import kg_io  # noqa: E402

DATA, FIG = ANALYSIS / "data", ANALYSIS / "figures"
UP, DOWN, NS, INK, MUTED, GREY_UP, GREY_DN = "#eb6834", "#2a78d6", "#d9d8d4", "#1f1f1d", "#6b6b66", "#b0afa9", "#77766f"
EXTENDED = {"10.64898/2026.04.15.718746_extended_light_med4", "10.64898/2026.04.15.718746_extended_darkness_med4"}
C2_EXPS = ["10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray",
           "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture",
           "10.1038/ismej.2011.49_iron_iron_starvation_med4_med4_microarray_light",
           "10.1038/nature06130_viral_phage_infected_med4_microarray"]


def parse_hours(label: str):
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


def read(p):
    """Read a CSV; display overrides (A.3-A.6: labels and grouping only) applied in memory."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import display_overrides as dov
    return dov.drop(dov.apply(pd.read_csv(p, encoding="utf-8", keep_default_na=False, na_values=[""])))   # A.8: 2016 coculture dropped


def main():
    ex = kg_io.load_experiments()
    tp_ = pd.read_csv(DATA / "explore_twin_pairs.csv", encoding="utf-8")   # from 12_twin_pairs.py
    global TWINS
    TWINS = list(zip(tp_.gene_a, tp_.gene_b))
    sets = kg_io.load_gene_sets()
    set_names = ["hli"] + kg_io.COMPARISON_SETS
    t = read(DATA / "hli_tests.csv")
    tps = t[["experiment_id", "timepoint"]].drop_duplicates()
    lab = tps.assign(hours=tps.timepoint.map(parse_hours))
    lab.merge(ex[["experiment_id", "label"]], on="experiment_id").to_csv(DATA / "explore_timing_labels.csv",
                                                                         index=False, encoding="utf-8")
    n_axis = lab.dropna(subset=["hours"]).groupby("experiment_id").size()
    chosen = sorted(set(n_axis[n_axis >= 3].index) | EXTENDED)
    with GraphConnection() as conn:
        genome = kg_io.fetch_genome(conn)
        de_all = {e: kg_io.fetch_de(e, conn) for e in chosen}
    tidx = t.set_index(["experiment_id", "timepoint", "set", "direction"])
    rows = []
    for e in chosen:
        exp = ex.set_index("experiment_id").loc[e]
        grid = hs.build_test_grid(de_all[e])
        for tp, g in grid.groupby("timepoint", sort=False):
            gu = g.set_index("direction")
            bg, _ = hs.main_background(exp.test_type if exp.test_type != "descriptive" else "sound",
                                       gu.at["up", "measured_genes"], genome)
            calls = hs.gene_calls_from_background(gu.at["up", "sig_genes"], gu.at["down", "sig_genes"], bg)
            # twin rule (critic #1): in a significant-only table, an absent twin of a listed twin is not defined
            listed = set(gu.at["up", "measured_genes"])
            hli_calls = dict(calls)
            if _ == "genome_assumption":
                for a_, b_ in TWINS:
                    for x, y in ((a_, b_), (b_, a_)):
                        if x in listed and y not in listed:
                            hli_calls.pop(y, None)
            for s in set_names:
                cs = hli_calls if s == "hli" else calls
                c = [cs[x] for x in sets[s] if x in cs]
                n = len(c)
                ru, rd = tidx.loc[(e, tp, s, "up")], tidx.loc[(e, tp, s, "down")]
                rows.append(dict(experiment_id=e, label=exp.label, label_detailed=exp.label_detailed,
                                 group=exp.group, light_reading_group=exp.light_reading_group, timepoint=tp,
                                 hours=parse_hours(tp), n_timepoints_on_axis=int(n_axis.get(e, 0)),
                                 only_two_timepoints=e in EXTENDED, set=s, test_type=ru.test_type,
                                 n_measured=n, n_up=c.count("up"), n_down=c.count("down"),
                                 frac_up=c.count("up") / n if n else np.nan, frac_down=c.count("down") / n if n else np.nan,
                                 padj_up=ru.padj_bh, padj_down=rd.padj_bh, testable_up=bool(ru.testable),
                                 testable_down=bool(rd.testable), flags_up=ru.flags, flags_down=rd.flags,
                                 sig_up=bool(ru.testable and ru.padj_bh < 0.05),
                                 sig_down=bool(rd.testable and rd.padj_bh < 0.05)))
    import display_overrides as dov   # labels from experiments.csv get the A.3-A.6 display overrides
    tm = dov.apply(pd.DataFrame(rows)).sort_values(["experiment_id", "set", "hours"])
    # check: hli gene-level counts equal analysis/data/hli_gene_calls.csv
    gc = read(DATA / "hli_gene_calls.csv")
    chk = gc[gc.experiment_id.isin(chosen)].groupby(["experiment_id", "timepoint"]).call.agg(
        n_up=lambda x: (x == "up").sum(), n_down=lambda x: (x == "down").sum())
    mm = tm[tm.set == "hli"].set_index(["experiment_id", "timepoint"])[["n_up", "n_down"]].join(chk, rsuffix="_gc")
    assert (mm.n_up == mm.n_up_gc).all() and (mm.n_down == mm.n_down_gc).all()
    tm.to_csv(DATA / "explore_timing.csv", index=False, encoding="utf-8")

    # ---- per-experiment summary (hli)
    summ = []
    for e, g in tm[(tm.set == "hli") & tm.hours.notna()].groupby("experiment_id"):
        g = g.sort_values("hours")
        testable = g[g.testable_up | g.testable_down]
        hits = g[g.sig_up | g.sig_down]
        first = hits.iloc[0] if len(hits) else None
        earliest_t = testable.iloc[0] if len(testable) else None
        last = g.iloc[-1]
        first_dir = None if first is None else ("up" if first.sig_up and not first.sig_down else
                                                "down" if first.sig_down and not first.sig_up else "both")
        persists = (None if first is None else
                    bool((last.sig_up and first_dir in ("up", "both")) or (last.sig_down and first_dir in ("down", "both"))))
        pk = g.loc[g.frac_up.idxmax()] if (g.frac_up.notna().any() and g.frac_up.max() > 0) else None   # None if no gene up
        summ.append(dict(
            experiment_id=e, label=g.label.iloc[0], n_timepoints_on_axis=len(g),
            only_two_timepoints=bool(g.only_two_timepoints.iloc[0]),
            timepoints=" | ".join(g.timepoint), test_types=" | ".join(g.test_type),
            n_testable_timepoints=len(testable),
            earliest_testable_timepoint=None if earliest_t is None else earliest_t.timepoint,
            first_hit_timepoint=None if first is None else first.timepoint,
            first_hit_direction=first_dir,
            hit_at_earliest_testable=(None if earliest_t is None else
                                      bool(earliest_t.sig_up or earliest_t.sig_down)),
            hit_timepoints=" | ".join(f"{r.timepoint} ({'up' if r.sig_up else ''}{'/' if r.sig_up and r.sig_down else ''}{'down' if r.sig_down else ''})"
                                      for r in hits.itertuples()),
            peak_frac_up_timepoint=None if pk is None else pk.timepoint,
            peak_frac_up=None if pk is None else round(float(pk.frac_up), 3),
            last_timepoint=last.timepoint, last_timepoint_testable=bool(last.testable_up or last.testable_down),
            hit_persists_to_last_timepoint=persists,
            frac_up_by_time=" | ".join(f"{x:.2f}" for x in g.frac_up),
            frac_down_by_time=" | ".join(f"{x:.2f}" for x in g.frac_down)))
    summ = pd.DataFrame(summ)
    summ.to_csv(DATA / "explore_timing_summary.csv", index=False, encoding="utf-8")

    # ---- C1 small multiples
    order = summ.sort_values(["only_two_timepoints", "n_timepoints_on_axis"], ascending=[True, False]).experiment_id.tolist()
    nc = 4
    nr = int(np.ceil(len(order) / nc))
    fig, axes = plt.subplots(nr, nc, figsize=(3.3 * nc, 2.5 * nr), squeeze=False)
    for ax, e in zip(axes.flat, order):
        h = tm[(tm.experiment_id == e) & (tm.set == "hli") & tm.hours.notna()].sort_values("hours")
        r = tm[(tm.experiment_id == e) & (tm.set == "ribosomal_proteins") & tm.hours.notna()].sort_values("hours")
        days = h.hours.max() > 96
        x = h.hours / 24 if days else h.hours
        xr = r.hours / 24 if days else r.hours
        ax.plot(xr, r.frac_up, color=GREY_UP, lw=0.9, zorder=1)
        ax.plot(xr, r.frac_down, color=GREY_DN, lw=0.9, ls=(0, (1, 1)), zorder=1)
        for col, fcol, scol, tcol in ((UP, "frac_up", "sig_up", "testable_up"), (DOWN, "frac_down", "sig_down", "testable_down")):
            xs, ys, desc = x.values, h[fcol].values, (h.test_type == "descriptive").values
            for k in range(len(xs) - 1):
                ax.plot(xs[k:k + 2], ys[k:k + 2], color=col, lw=1.6, ls="--" if (desc[k] or desc[k + 1]) else "-", zorder=2)
            for xi, yi, sg, tb, ds in zip(xs, ys, h[scol], h[tcol], desc):
                if sg:
                    ax.plot(xi, yi, "o", ms=5.5, color=col, mec="white", mew=0.6, zorder=4)
                elif not tb:
                    ax.plot(xi, yi, "o", ms=5, mfc="white", mec=col, mew=1, zorder=3)
                else:
                    ax.plot(xi, yi, "o", ms=2.2, color=col, zorder=3)
        ttl = h.label.iloc[0] + (" (2 time points)" if e in EXTENDED else "")
        ax.set_title(ttl, fontsize=7.5, loc="left")
        ax.set_xlabel("days" if days else "hours", fontsize=7)
        ax.set_ylim(-0.03, 1.0)
        ax.tick_params(labelsize=6.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    for ax in list(axes.flat)[len(order):]:
        ax.set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel("share of measured\nset genes significant", fontsize=7)
    fig.legend(handles=[Line2D([], [], color=UP, lw=1.6, label="hli up"), Line2D([], [], color=DOWN, lw=1.6, label="hli down"),
                        Line2D([], [], color=GREY_UP, lw=0.9, label="ribosomal proteins up"),
                        Line2D([], [], color=GREY_DN, lw=0.9, ls=(0, (1, 1)), label="ribosomal proteins down"),
                        Line2D([], [], marker="o", ls="", color=MUTED, ms=5.5, label="hli set-level BH padj < 0.05"),
                        Line2D([], [], marker="o", ls="", mfc="white", mec=MUTED, ms=5, label="hli test not testable (too few / up-only)"),
                        Line2D([], [], color=MUTED, ls="--", label="descriptive table / time point")],
               loc="lower center", ncol=4, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("hli over time in MED4 time-course experiments: share of measured hli genes significant up and down "
                 "(treatment vs control, as stored)", fontsize=9.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(FIG / "explore_C1_timing.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_C1_timing.svg", bbox_inches="tight")
    plt.close(fig)

    # ---- C2 gene-level time heatmaps
    genes = gc[["locus_tag", "ck_group"]].drop_duplicates().sort_values(["ck_group", "locus_tag"])
    fig, axes = plt.subplots(1, len(C2_EXPS), figsize=(3.0 * len(C2_EXPS) + 1.5, 6.2), sharey=True,
                             gridspec_kw=dict(width_ratios=[max(3, gc[gc.experiment_id == e].timepoint.nunique()) for e in C2_EXPS]))
    for ax, e in zip(axes, C2_EXPS):
        g = gc[gc.experiment_id == e].copy()
        g["hours"] = g.timepoint.map(parse_hours)
        g = g.dropna(subset=["hours"])
        tps_ = g[["timepoint", "hours", "test_type"]].drop_duplicates().sort_values("hours")
        gi = g.set_index(["locus_tag", "timepoint"])
        for j, tp in enumerate(tps_.itertuples()):
            for i, gn in enumerate(genes.itertuples()):
                call = gi.at[(gn.locus_tag, tp.timepoint), "call"]
                if call == "not_measured":
                    ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor="white"))
                    ax.add_patch(Rectangle((j + .1, i + .1), .8, .8, facecolor="none", edgecolor="#c9c8c3", hatch="////", lw=0))
                else:
                    ax.add_patch(Rectangle((j, i), 1, 1, facecolor={"up": UP, "down": DOWN, "ns": NS}[call],
                                           edgecolor="white", lw=0.8))
        ax.set_xlim(0, len(tps_))
        ax.set_ylim(len(genes), 0)
        ax.set_xticks(np.arange(len(tps_)) + .5)
        ax.set_xticklabels([f"{t_}{' (d)' if ty == 'descriptive' else ''}" for t_, ty in zip(tps_.timepoint, tps_.test_type)],
                           rotation=90, fontsize=6.5)
        ax.set_title(g.label.iloc[0], fontsize=8, loc="left")
        ax.tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
    axes[0].set_yticks(np.arange(len(genes)) + .5)
    axes[0].set_yticklabels([f"{r.locus_tag} ({r.ck_group.split(':')[-1]})" for r in genes.itertuples()], fontsize=6.5)
    axes[-1].legend(handles=[Patch(facecolor=UP, label="up"), Patch(facecolor=DOWN, label="down"),
                             Patch(facecolor=NS, label="not significant"),
                             Patch(facecolor="white", edgecolor="#c9c8c3", hatch="////", label="not measured")],
                    loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=7, frameon=False)
    fig.suptitle("hli genes over time (time points in time order; treatment vs control, as stored)", fontsize=9.5,
                 x=0.01, ha="left")
    fig.text(0.01, -0.02, "lowN coculture: each day vs the same series on day 11; the pooled 'days 60+89' is not shown. "
             "Phage infection array: up-only table (absent genes = not significant).", fontsize=6.5, color=MUTED)
    fig.savefig(FIG / "explore_C2_gene_time.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_C2_gene_time.svg", bbox_inches="tight")
    plt.close(fig)
    pd.set_option("display.width", 260)
    pd.set_option("display.max_colwidth", 80)
    print(summ.drop(columns=["experiment_id"]).to_string(index=False))
    print("unparsed labels:", lab[lab.hours.isna()].timepoint.unique().tolist())
    print("chosen:", len(chosen))


if __name__ == "__main__":
    main()
