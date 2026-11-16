"""Exploration A: hli gene families (CK group; multi- vs single-copy class).

Copy class: a CK group with >= 2 MED4 hli members is multi-copy, the rest single-copy
(membership from methods/data/gene_sets.csv). Calls are the gene-level calls in
analysis/data/hli_gene_calls.csv (study significance calls; absent genes in significant-only
tables = ns on the genome background; absent genes in full / top-N tables = not measured).

Writes analysis/data/explore_families.csv (per experiment x timepoint x family, CK groups and the
two copy classes) and analysis/data/explore_families_scope.csv (per family x reading scope;
descriptive time points - N-depleted top-50%, phosphate 0-24 h, pooled lowN 'days 60+89' - are
left out of the scope totals). Figures: analysis/figures/explore_A1_ck_groups_net.{png,svg},
explore_A2_copy_class.{png,svg}.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/04_explore_families.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
DATA, FIG = ANALYSIS / "data", ANALYSIS / "figures"
UP, DOWN, MID, INK, MUTED, GRID = "#eb6834", "#2a78d6", "#f0efec", "#1f1f1d", "#6b6b66", "#d9d8d4"
CMAP = LinearSegmentedColormap.from_list("spock_diverging", [DOWN, MID, UP])
BLOCK_ORDER = ["light_onset", "constant_dark_vs_light", "schedule_extension", "electron_transport_DCMU",
               "phage_dark", "nonlight_stress", "nonstress_possible_relief"]
BLOCK_LABEL = {"light_onset": "Light onset", "constant_dark_vs_light": "Constant dark vs light",
               "schedule_extension": "Schedule extension", "electron_transport_DCMU": "DCMU",
               "phage_dark": "Phage, dark", "nonlight_stress": "Non-light stress",
               "nonstress_possible_relief": "Non-stress / possible relief"}
SCOPES = [("light_reading_group", "light_onset", "Light onset"),
          ("light_reading_group", "constant_dark_vs_light", "Const. dark\nvs light"),
          ("light_reading_group", "schedule_extension", "Schedule\nextension"),
          ("light_reading_group", "electron_transport_DCMU", "DCMU"),
          ("light_reading_group", "phage_dark", "Phage, dark"),
          ("nonlight_stress_type", "carbon", "CO2"), ("nonlight_stress_type", "iron", "Iron"),
          ("nonlight_stress_type", "nitrogen", "Nitrogen"), ("nonlight_stress_type", "phosphorus", "Phosphorus"),
          ("nonlight_stress_type", "salt", "Salt"), ("nonlight_stress_type", "viral", "Phage, light"),
          ("group", "nonstress_possible_relief", "Non-stress")]


def read(p):
    return pd.read_csv(p, encoding="utf-8", keep_default_na=False, na_values=[""])


def save(fig, stem):
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def summarise(g):
    meas = g[g.call != "not_measured"]
    n, nu, nd = len(meas), int((meas.call == "up").sum()), int((meas.call == "down").sum())
    return dict(n_genes=len(g), n_measured=n, n_up=nu, n_down=nd, frac_up=nu / n if n else np.nan,
                frac_down=nd / n if n else np.nan, net_share=(nu - nd) / n if n else np.nan)


def in_scope(df, st, sc):
    if st == "light_reading_group":
        return df.light_reading_group == sc
    if st == "nonlight_stress_type":
        return (df.group == "nonlight_stress") & (df.stress_type == sc)
    return df.group == sc


def main():
    gs = read(ANALYSIS.parent / "methods" / "data" / "gene_sets.csv")
    grp = gs[gs.set.str.startswith("hli_group:")].assign(ck_group=lambda x: x.set.str.split(":").str[-1])
    size = grp.groupby("ck_group").locus_tag.nunique()
    copy_class = {g: ("multi_copy" if n >= 2 else "single_copy") for g, n in size.items()}
    gc = read(DATA / "hli_gene_calls.csv")
    gc["ck"] = gc.ck_group.str.split(":").str[-1]
    gc["copy_class"] = gc.ck.map(copy_class)
    assert gc.copy_class.notna().all()
    keys = ["experiment_id", "label", "label_detailed", "group", "light_reading_group", "stress_type", "timepoint",
            "timepoint_order", "test_type", "light_treatment_umol"]
    rows = []
    for k, g in gc.groupby(keys, sort=False):
        base = dict(zip(keys, k))
        for fam, f in g.groupby("ck"):
            rows.append({**base, "family_type": "ck_group", "family": fam, "copy_class": copy_class[fam],
                         "family_size": int(size[fam]), **summarise(f)})
        for cc, f in g.groupby("copy_class"):
            rows.append({**base, "family_type": "copy_class", "family": cc, "copy_class": cc,
                         "family_size": int(f.locus_tag.nunique()), **summarise(f)})
    fam = pd.DataFrame(rows)
    fam.to_csv(DATA / "explore_families.csv", index=False, encoding="utf-8")

    # scope totals: gene x experiment-timepoint observations, descriptive time points excluded
    gc_t = gc[gc.test_type != "descriptive"]
    srows = []
    for ftype, col in (("ck_group", "ck"), ("copy_class", "copy_class")):
        for f, gf in gc_t.groupby(col):
            for st, sc, lab in SCOPES:
                g = gf[in_scope(gf, st, sc)]
                s = summarise(g)
                srows.append(dict(family_type=ftype, family=f, family_size=(int(size[f]) if ftype == "ck_group"
                                                                            else int(gf.locus_tag.nunique())),
                                  scope_type=st, scope=sc, n_experiment_timepoints=g[["experiment_id", "timepoint"]]
                                  .drop_duplicates().shape[0], n_gene_observations=s["n_measured"],
                                  n_up=s["n_up"], n_down=s["n_down"], frac_up=s["frac_up"], frac_down=s["frac_down"]))
    sc_df = pd.DataFrame(srows)
    sc_df.to_csv(DATA / "explore_families_scope.csv", index=False, encoding="utf-8")

    # ---- A1: CK groups x experiment-timepoints, net share
    ck = fam[fam.family_type == "ck_group"].copy()
    cols = ck[keys].drop_duplicates(["experiment_id", "timepoint"]).copy()
    cols["block"] = [lr if lr != "none" else g for lr, g in zip(cols.light_reading_group, cols.group)]
    cols["rank"] = cols.block.map({b: i for i, b in enumerate(BLOCK_ORDER)})
    cols = cols.sort_values(["rank", "label", "timepoint_order"]).reset_index(drop=True)
    fams = sorted(size.index, key=lambda f: (-size[f], f))
    idx = ck.set_index(["experiment_id", "timepoint", "family"])
    norm = TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)
    fig, ax = plt.subplots(figsize=(0.2 * len(cols) + 3.5, 0.3 * len(fams) + 2))
    for j, c in enumerate(cols.itertuples()):
        for i, f in enumerate(fams):
            r = idx.loc[(c.experiment_id, c.timepoint, f)]
            if r["n_measured"] == 0:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor="white", lw=0.8))
                ax.add_patch(Rectangle((j + .08, i + .08), .84, .84, facecolor="none", edgecolor="#c9c8c3",
                                       hatch="////", lw=0))
            else:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=CMAP(norm(r["net_share"])), edgecolor="white", lw=0.8))
        if c.test_type == "descriptive":
            ax.text(j + .5, len(fams) + .15, "d", ha="center", va="top", fontsize=5, color=MUTED)
    for i in range(1, len(fams)):
        if copy_class[fams[i]] != copy_class[fams[i - 1]]:
            ax.axhline(i, color=INK, lw=1.4)
    blocks = cols.block.tolist()
    s0 = 0
    for j in range(1, len(cols) + 1):
        if j == len(cols) or blocks[j] != blocks[s0]:
            if j < len(cols):
                ax.axvline(j, color=INK, lw=0.9)
            lab = BLOCK_LABEL[blocks[s0]]
            ax.text((s0 + j) / 2, -0.3, lab if j - s0 > 6 else lab.replace(" ", "\n"), ha="center", va="bottom",
                    fontsize=6, color=INK)
            s0 = j
    ax.set_xlim(0, len(cols))
    ax.set_ylim(len(fams) + .6, 0)
    ax.set_yticks(np.arange(len(fams)) + .5)
    ax.set_yticklabels([f"{f} (n={size[f]}, {copy_class[f].replace('_', '-')})" for f in fams], fontsize=6.5)
    ax.set_xticks(np.arange(len(cols)) + .5)
    ax.set_xticklabels([f"{a} · {b}" for a, b in zip(cols.label, cols.timepoint)], rotation=90, fontsize=5.2)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=CMAP, norm=norm), ax=ax, fraction=0.015, pad=0.01, shrink=0.7)
    cb.set_label("net share = (up − down) / measured\n← more down · more up →", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    ax.set_title("hli CK groups (MED4): net share of measured members significant up minus down, per experiment × time point",
                 fontsize=9, loc="left", pad=36)
    ax.annotate("Rows: multi-copy groups (≥2 MED4 members) above the line, single-copy below. Hatched = no member measured. "
                "d = descriptive time point. Treatment vs control, as stored in the KG (no flip).",
                xy=(0, 0), xycoords="axes fraction", xytext=(0, -215), textcoords="offset points", fontsize=6,
                color=MUTED, va="top")
    save(fig, FIG / "explore_A1_ck_groups_net")

    # ---- A2: multi vs single copy, fraction up / down per scope (diverging bars)
    cc = sc_df[sc_df.family_type == "copy_class"].set_index(["family", "scope_type", "scope"])
    fig, ax = plt.subplots(figsize=(10, 4.2))
    x = np.arange(len(SCOPES))
    w = 0.36
    nm = {c: (sum(1 for g in size.index if copy_class[g] == c), int(sum(size[g] for g in size.index if copy_class[g] == c)))
          for c in ("multi_copy", "single_copy")}
    for k, (fam_, hatch) in enumerate((("multi_copy", None), ("single_copy", "////"))):
        off = (k - 0.5) * w
        fu = [cc.loc[(fam_, st, sc), "frac_up"] for st, sc, _ in SCOPES]
        fd = [cc.loc[(fam_, st, sc), "frac_down"] for st, sc, _ in SCOPES]
        n = [int(cc.loc[(fam_, st, sc), "n_gene_observations"]) for st, sc, _ in SCOPES]
        ax.bar(x + off, np.nan_to_num(fu), w * 0.92, color=UP, hatch=hatch, edgecolor="white", lw=0.5)
        ax.bar(x + off, -np.nan_to_num(fd), w * 0.92, color=DOWN, hatch=hatch, edgecolor="white", lw=0.5)
        for xi, ni, u in zip(x + off, n, fu):
            ax.text(xi, (u if not np.isnan(u) else 0) + 0.02, f"{ni}", ha="center", va="bottom", fontsize=5.5, color=MUTED)
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([l for _, _, l in SCOPES], fontsize=7)
    ax.set_ylabel("share of measured gene observations\n← significant down · significant up →", fontsize=8)
    yt = ax.get_yticks()
    ax.set_yticks(yt)
    ax.set_yticklabels([f"{abs(v):.1f}" for v in yt], fontsize=7)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(handles=[Patch(facecolor=MUTED, label=f"multi-copy (solid; {nm['multi_copy'][1]} genes in {nm['multi_copy'][0]} CK groups)"),
                       Patch(facecolor=MUTED, hatch="////", edgecolor="white",
                             label=f"single-copy (hatched; {nm['single_copy'][1]} genes in {nm['single_copy'][0]} CK groups)")],
              fontsize=7, frameon=False, loc="upper right")
    ax.set_title("hli copy class: share of measured gene × time-point observations significant up (orange) and down (blue), "
                 "per reading scope", fontsize=9, loc="left")
    ax.annotate("Numbers = measured gene observations. Descriptive time points excluded. Treatment vs control (no flip).",
                xy=(0, 0), xycoords="axes fraction", xytext=(0, -40), textcoords="offset points", fontsize=6.5,
                color=MUTED, va="top")
    save(fig, FIG / "explore_A2_copy_class")
    print(sc_df[sc_df.family_type == "copy_class"].to_string(index=False))
    print("copy classes:", {k: v for k, v in copy_class.items()}, "sizes:", size.to_dict())


if __name__ == "__main__":
    main()
